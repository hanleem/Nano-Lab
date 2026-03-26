# Nano Lab MVP (FastAPI)

Quick MVP backend for a workflow that includes:
- project setup/activation
- requirement/task management
- document upload + placeholder OCR extraction
- text comparison analysis
- CSV/PDF-like export endpoints
- project dashboard summary

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
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
