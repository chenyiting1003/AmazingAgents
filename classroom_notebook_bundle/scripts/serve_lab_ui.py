#!/usr/bin/env python3
"""
Lab UI: serves web/ static files, output read APIs, and POST /api/continue for student-led rounds.

Local use:
  python scripts/serve_lab_ui.py
  Open http://127.0.0.1:8080

Requires packages from requirements.txt for continuation (openai, python-dotenv).
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
OUTPUTS_DIR = ROOT / "outputs"

OUTPUT_FILES = {
    "/api/outputs/transcript": OUTPUTS_DIR / "model_un_transcript.json",
    "/api/outputs/variables": OUTPUTS_DIR / "model_un_variables.json",
    "/api/outputs/report": OUTPUTS_DIR / "model_un_simulation_report.md",
    "/api/outputs/role_leakage": OUTPUTS_DIR / "model_un_role_leakage_report.md",
}


def _continuation_module():
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        import lab_continue as lc  # type: ignore

        return lc
    except ImportError as e:
        return e


def _under_dir(base: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


class LabUIHandler(BaseHTTPRequestHandler):
    server_version = "LabUI/1.1"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[serve_lab_ui] {self.address_string()} - {fmt % args}")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path != "/api/continue":
            self._send(404, b"Not Found", "text/plain; charset=utf-8")
            return

        lc = _continuation_module()
        if isinstance(lc, Exception):
            err = json.dumps(
                {
                    "ok": False,
                    "error": f"Continuation unavailable: {lc}. Run: pip install -r requirements.txt",
                },
                ensure_ascii=False,
            ).encode("utf-8")
            self._send(500, err, "application/json; charset=utf-8")
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length > 96_000:
            self._send(
                413,
                json.dumps({"ok": False, "error": "Request body too large"}).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(
                400,
                json.dumps({"ok": False, "error": "Invalid JSON body"}).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return

        instruction = str(payload.get("instruction") or "")
        agents = payload.get("agents")
        if agents is not None and not isinstance(agents, list):
            self._send(
                400,
                json.dumps({"ok": False, "error": "agents must be an array of strings or omitted"}).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        agent_list = [str(a) for a in agents] if agents is not None else None

        result = lc.run_continuation(instruction=instruction, agents=agent_list, root=ROOT)
        code = 200 if result.get("ok") else 400
        self._send(code, json.dumps(result, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/api/outputs/status":
            cont_path = OUTPUTS_DIR / "model_un_student_continuations.json"
            status = {
                "transcript": OUTPUT_FILES["/api/outputs/transcript"].is_file(),
                "report": OUTPUT_FILES["/api/outputs/report"].is_file(),
                "variables": OUTPUT_FILES["/api/outputs/variables"].is_file(),
                "role_leakage": OUTPUT_FILES["/api/outputs/role_leakage"].is_file(),
                "continuations": cont_path.is_file() and cont_path.stat().st_size > 50,
            }
            body = json.dumps(status, ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
            return

        if path == "/api/outputs/continuations":
            lc = _continuation_module()
            if isinstance(lc, Exception):
                self._send(
                    500,
                    json.dumps({"error": str(lc)}, ensure_ascii=False).encode("utf-8"),
                    "application/json; charset=utf-8",
                )
                return
            data = lc.load_continuations(ROOT)
            self._send(200, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            return

        if path in OUTPUT_FILES:
            fp = OUTPUT_FILES[path]
            if not fp.is_file():
                self._send(
                    404,
                    json.dumps({"error": "file not found", "path": str(fp.name)}).encode("utf-8"),
                    "application/json; charset=utf-8",
                )
                return
            raw = fp.read_bytes()
            if path.endswith("transcript") or path.endswith("variables"):
                self._send(200, raw, "application/json; charset=utf-8")
            else:
                self._send(200, raw, "text/plain; charset=utf-8")
            return

        rel = path.lstrip("/")
        if not rel or rel.endswith("/"):
            rel = "index.html"

        candidate = (WEB_DIR / rel).resolve()
        if not _under_dir(WEB_DIR.resolve(), candidate) or not candidate.is_file():
            self._send(404, b"Not Found", "text/plain; charset=utf-8")
            return

        ctype, _ = mimetypes.guess_type(str(candidate))
        if not ctype:
            ctype = "application/octet-stream"
        body = candidate.read_bytes()
        self._send(200, body, ctype)


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve lab web UI and outputs API.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (use 0.0.0.0 to listen on all interfaces)")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port")
    args = parser.parse_args()

    if not WEB_DIR.is_dir():
        print(f"ERROR: Missing web directory: {WEB_DIR}")
        return 1

    httpd = HTTPServer((args.host, args.port), LabUIHandler)
    print(f"Lab UI: http://{args.host}:{args.port}/")
    print("  GET  /api/outputs/status | transcript | report | variables | role_leakage | continuations")
    print('  POST /api/continue  JSON { "instruction": "...", "agents": ["..."] optional }')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
