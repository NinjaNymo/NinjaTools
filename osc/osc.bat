@echo off
REM Wrapper for osc.py to run from Windows CMD with arguments

cd /d "%~dp0"
python osc.py %*
