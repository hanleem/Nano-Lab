# Nano Lab MVP (FastAPI)

Quick MVP backend for a workflow that includes:
- project setup/activation
- requirement/task management
- document upload + placeholder OCR extraction
- text comparison analysis
- CSV/PDF-like export endpoints
- project dashboard summary

## Requirements
- Python 3.10+

## Run on Windows (PowerShell)

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

If PowerShell blocks activation scripts, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again.

## Run on Windows (cmd)

```bat
py -3.10 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e ".[dev]"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Run on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

## Main endpoints
- `POST /projects`
- `PATCH /projects/{id}/activate`
- `POST /projects/{id}/requirements`
- `GET /projects/{id}/requirements/export.csv`
- `GET /projects/{id}/requirements/export.pdf`
- `POST /projects/{id}/documents`
- `POST /analysis/compare`
- `GET /projects/{id}/dashboard`

## Notes
- OCR/PDF generation is MVP placeholder logic intended to be replaced with real integrations.
