@echo off
setlocal
cd /d "%~dp0.."
python scripts\student_run_lab.py %*
pause
