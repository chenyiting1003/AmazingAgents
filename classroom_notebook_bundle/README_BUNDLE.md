# Mini Model UN — classroom notebook bundle (self-contained folder)

This directory includes: the notebook entry point, case materials, core `scripts/`, the `web/` lab UI, student docs, and `docs/`.

## Quick start

1. Copy this folder anywhere (keep internal structure).
2. `cp .env.example .env` and fill in API settings per your class (template defaults to DeepSeek).
3. `python -m venv .venv` → activate → `pip install -r requirements.txt`.
4. Open **`Mini_Model_UN_Student_Lab.ipynb`** in Jupyter / VS Code / Cursor and run cells top to bottom.

Full English walkthrough: **`docs/STUDENT_LAB_GUIDE.md`**.

**Do not commit `.env`; never post API keys in public chat.**
