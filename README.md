# Daylist backend

This folder holds the local FastAPI backend for the Daylist to-do app.

## 1) Open PowerShell in the backend folder

```powershell
cd C:\path\to\todo-list-backend\backend
```

This changes into the backend project directory so the app and tests run from the right place.

## 2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

The first command creates a local Python environment named `.venv`. The second command activates it so packages are installed only for this project, not globally on your computer.

## 3) Install the requirements

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

These commands install FastAPI, Uvicorn, Pytest, and HTTPX in the virtual environment.

## 4) Run the API

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

This starts the local API server. While it is running, you can open the interactive docs page at http://127.0.0.1:8000/docs.

## 5) Run the tests

```powershell
pytest -q
```

This runs the backend test suite and checks the API behavior.

## Database note

The SQLite database is stored locally on this computer in the `data` folder and should not be committed to Git. If you ever want to use a different local frontend port, add the exact origin to the `allow_origins` list in `app/main.py`.

Example:

```python
allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"]
```

This keeps CORS limited to the local Vite origins the app actually needs.
