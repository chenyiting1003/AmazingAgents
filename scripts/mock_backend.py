#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ["/", "/health", "/api/health"]:
            self._send(200, {"status": "ok", "service": "mirofish-classroom-backend"})
        else:
            self._send(404, {"error": "not found"})

HTTPServer(("0.0.0.0", 5001), Handler).serve_forever()
