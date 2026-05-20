# Classroom workflow (Python + browser)

1. Students clone the repo and create `.env` from `.env.example`.
2. They create a virtual environment, `pip install -r requirements.txt`.
3. They run `python scripts/student_run_lab.py` (or `run_minisim.py`) to generate `outputs/`.
4. They run `python scripts/serve_lab_ui.py` and open **http://127.0.0.1:8080/** to review results and optionally use **继续讨论**.
5. Discussion and validity critique use `docs/validity_critique_template.md` and `case_materials/classroom_tasks.md` as assigned.
