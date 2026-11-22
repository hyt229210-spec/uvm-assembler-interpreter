@echo off

set "ROOT=%~dp0"

if not exist "%ROOT%.venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Run: py -m venv .venv
    exit /b 1
)

"%ROOT%.venv\Scripts\python.exe" "%ROOT%src\assembler.py" %*

exit /b %ERRORLEVEL%