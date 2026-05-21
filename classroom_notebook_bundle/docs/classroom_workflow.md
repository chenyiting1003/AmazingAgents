# Classroom workflow (DeepSeek by default, Jupyter-only path for students)

1. Students clone the repo and create `.env` from `.env.example` (**defaults target DeepSeek**).
2. They create a virtual environment, `pip install -r requirements.txt`.
3. They open **`Mini_Model_UN_Student_Lab.ipynb`** and run cells through baseline → **Start lab UI** → `outputs/` + **http://127.0.0.1:8080/**.
4. Discussion and validity critique use `docs/validity_critique_template.md` and `case_materials/classroom_tasks.md` as assigned.

(Engines: `scripts/run_minisim.py`, `scripts/serve_lab_ui.py`, `scripts/lab_continue.py` — same code path as manual `python` when debugging.)
