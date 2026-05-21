# AmazingAgents · LLM social simulation (classroom lab)

HKUST(GZ) AI + society lab repo: **DeepSeek API by default** (OpenAI-compatible), **Jupyter notebook as the main path**; underneath it still runs `scripts/run_minisim.py` and `scripts/serve_lab_ui.py` (same implementation as the CLI).

- **Classroom entry:** [`Mini_Model_UN_Student_Lab.ipynb`](Mini_Model_UN_Student_Lab.ipynb) — **first cell = usage guide**
- **English student walkthrough:** [`docs/STUDENT_LAB_GUIDE.md`](docs/STUDENT_LAB_GUIDE.md)
- **Short student README:** [`README_STUDENTS.md`](README_STUDENTS.md)
- **Instructor notes:** [`README_INSTRUCTOR.md`](README_INSTRUCTOR.md)

```bash
pip install -r requirements.txt
# Open Mini_Model_UN_Student_Lab.ipynb in Jupyter / VS Code / Cursor and run top to bottom.

# Advanced: debug only from project root (not the main classroom path)
python scripts/run_minisim.py
python scripts/serve_lab_ui.py
```
