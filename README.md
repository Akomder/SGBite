# SaigonBite

Flask starter for the RAD SaigonBite project. It follows the agreed layers: Jinja views, Flask controllers, domain rules, and SQLAlchemy repositories/models.

## Requirements

- Python 3.12+
- Git
- Docker Desktop for PostgreSQL (SQLite is the local default)

## Run locally (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
flask --app app run --debug
```

Open `http://127.0.0.1:5000/health`; the starter returns `{"status":"ok"}`. SQLite is used by default. To use PostgreSQL, run `docker compose up -d db` and set `DATABASE_URL` in `.env` to:

```text
postgresql+psycopg://saigonbite:saigonbite@localhost:5432/saigonbite
```

## Project layout

```text
app/controller/  Flask blueprints for orders, vouchers, and reports
app/data/        SQLAlchemy setup, models, and repositories
app/domain/      Order lifecycle and voucher rules
app/view/        Jinja templates and static assets
docs/models/     PlantUML / diagrams.net sources
sql/             schema and sample data scripts
```

## Starter endpoints

- `GET /health` and `GET /`
- `POST /orders` to place an order
- `POST /orders/<id>/decision` with `{"decision":"confirm"}` or `{"decision":"reject","reason":"..."}`
- `GET /vouchers` and `POST /vouchers`
- `GET /reports/summary`

The scaffold still needs authentication and authorization, menu/hub reference data, full voucher CRUD, richer reporting, migrations, and the remaining coursework artifacts. Review all business rules against the case study and client answers before treating them as final.

## Git collaboration

Use one branch per assigned use case (`uc1-place-order`, `uc2-confirm-reject`, `uc3-vouchers`, `uc4-reports`). Commit your own work with a use-case prefix and review each other's pull requests. Do not commit `.env`, credentials, or local database files.
