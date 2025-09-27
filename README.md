Project Kelebek

Setup instructions

1. Use a 64-bit Python 3.8+ interpreter
- In PyCharm: File > Settings > Project > Python Interpreter and select your existing venv or create a new one. Avoid references to Python38-32 (32-bit). If you see an invalid path like AppData\Local\Programs\Python\Python38-32\python.exe, remove it and select a valid 64-bit Python.

2. Install dependencies
- From the project root, run: pip install -r requirements.txt
- If pycountry fails to build, try: pip install --no-cache-dir --use-pep517 pycountry
- Some packages (graphviz, pyodbc) may require system dependencies:
  - Graphviz: install Graphviz from https://graphviz.org/download/ and ensure its bin folder is on PATH.
  - pyodbc: ensure the appropriate ODBC drivers are installed for your database and Python architecture.

Notes on requirements
- Cleaned duplicates and fixed package names (openpyxl, pillow) to improve install reliability.
- Replaced deprecated pycrypto with pycryptodome.
- cx-Freeze name normalized.

Running the app
- Launch main.py with the selected interpreter.


Quick install (Windows)
- From File Explorer, double-click scripts\install.bat (or right-click scripts\install.ps1 and choose "Run with PowerShell").
- Optional: to create and use a local virtual environment, run from a PowerShell in the project root:
  - .\scripts\install.ps1 -CreateVenv
- The script upgrades pip/setuptools/wheel and installs requirements.txt. See notes for Graphviz and pyodbc system dependencies.
