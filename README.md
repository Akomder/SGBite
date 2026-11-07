# SaigonBite OFDH Prototype

SaigonBite is a Flask prototype of an Online Food Delivery Hub (OFDH), built for the RAD final project (Semester 1, 2026–2027). It brings four team use cases into one web application: customers place and track orders, kitchen staff confirm or reject incoming orders, admins manage vouchers, and managers view operational reports.

## Features

- Customer ordering from a selected hub, with item availability, delivery distance, hub capacity, delivery pricing, and voucher checks.
- Order preview and placement, order history, and cancellation while the order is still eligible.
- Kitchen queue scoped to the staff member's hub, with confirm, reject, and order progression actions.
- Voucher creation, search, editing, deactivation, and redemption limits.
- Sales, hub workload, and delivery performance reports, with CSV export.
- English and Vietnamese customer-facing labels, with the default language selected by customer type.
- SQLite for local development; PostgreSQL support through Docker Compose.

## Requirements

- Python 3.12 or newer for local development.
- Docker Desktop (or Docker Engine with Compose) for the containerized PostgreSQL setup.

## Run locally with SQLite

Create a virtual environment, install dependencies, initialize the database with demo data, and start Flask:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
flask --app app init-db
flask --app app run --debug
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead. Open <http://127.0.0.1:5000>.

The default database is `saigonbite.db` in the project directory. `flask --app app init-db` creates the tables and sample records only when the database is empty. To initialize tables without the demo orders, run `flask --app app init-db --no-demo`.

## Run with Docker Compose and PostgreSQL

Build and start the web app and database:

```bash
docker compose up --build
```

Open <http://localhost:8000>. The container starts the database, initializes it with sample data if empty, and serves the app with Gunicorn. Stop the services with `docker compose down`. The database is stored in the `dbdata` Docker volume and remains after stopping the containers.

To run Flask on your machine while using only the Docker database, start the database service:

```bash
docker compose up -d db
```

Then set `DATABASE_URL` and initialize/run the app:

```powershell
# PowerShell
$env:DATABASE_URL = "postgresql+psycopg://saigonbite:saigonbite@localhost:5432/saigonbite"
flask --app app init-db
flask --app app run --debug
```

```bash
# macOS/Linux
export DATABASE_URL=postgresql+psycopg://saigonbite:saigonbite@localhost:5432/saigonbite
flask --app app init-db
flask --app app run --debug
```

`.env.example` documents the local environment variables. Flask does not load that file automatically; export the variables in your shell or use a local environment-file loader if desired.

## Demo accounts

All seeded accounts use the development password `password`.

| Username | Role | Notes |
|---|---|---|
| `an` | Customer | Local customer; Vietnamese labels by default. |
| `tourist` | Customer | Tourist customer; English labels by default. |
| `kitchen1` | Kitchen staff | Hub District 1. |
| `kitchen2` | Kitchen staff | Hub Thu Duc. |
| `admin` | Admin | Manages vouchers. |
| `manager` | Manager | Views reports and CSV exports. |

Demo voucher codes include `WELCOME10` (10% off eligible item subtotals), `SAVE20K` (20,000 VND off eligible item subtotals), and `OLD5` (expired example).

## Project structure

```text
app/
  controller/    Flask blueprints for authentication, ordering, kitchen, vouchers, reports
  data/          SQLAlchemy setup, repositories, and seed data
  domain/        Persistent models and business rules/services
  view/          Jinja templates, translations, and CSS
docs/
  traceability.md  Requirement-to-code-to-test mapping
sql/
  create_database.sql  PostgreSQL database/user setup script
  schema.sql           PostgreSQL schema export
  data.sql             PostgreSQL sample-data export
tests/                 Pytest coverage for domain rules, use cases, pages, and integration
scripts/
  export_schema.py     Generate the PostgreSQL schema export
```

The application follows a layered design: views call controllers, controllers coordinate domain services, and repositories in `app/data/repositories.py` run database queries. Domain rules are kept out of controllers.

## Use cases

| Use case | Owner | Main implementation |
|---|---|---|
| UC1 Place an order | MOUNTHADY SOUK AKHOM (523K0076) | `app/domain/ordering.py`, `app/controller/ordering.py` |
| UC2 Confirm or reject an incoming order | Dang Doan Minh Tan (523V0017) | `app/domain/kitchen.py`, `app/controller/kitchen.py` |
| UC3 Manage vouchers | MOUNTHADY SOUK AKHOM (523K0076) | `app/domain/vouchers.py`, `app/controller/vouchers.py` |
| UC4 Produce management reports | Dang Doan Minh Tan (523V0017) | `app/domain/reports.py`, `app/controller/reports.py` |

See [the traceability guide](docs/traceability.md) for requirement, code, and test links.

## Business rules represented

- Delivery is limited to 7 km, with fee bands of 15,000, 25,000, or 35,000 VND.
- Rain mode adds 10,000 VND; a quiet hub can reduce the delivery fee by 5,000 VND.
- Hub load is based on confirmed and preparing orders; the app warns at 80% capacity and stops accepting orders when full.
- Customers can cancel while an order is Placed or Confirmed. Online payments are marked refunded after rejection or cancellation; cash is not charged.
- A voucher applies to item subtotal only, with one voucher per order and one redemption per customer when configured.
- Reports use stored order data; an order is late when delivery takes over 45 minutes.

## Scope and limitations

- Payment processing, notifications, and maps are simulated. Customers enter the delivery distance themselves.
- The seed data creates customers, hubs, brands, menu items, vouchers, and demo orders; there are no management screens for those records.
- Shipper and office staff roles are outside the implemented use cases. Kitchen staff can advance orders through delivery states to support the workflow and reporting.
- Customer-facing labels are available in English and Vietnamese; error messages are English only.
- Performance and availability targets have not been load-tested. PostgreSQL support is provided, while the automated test suite uses SQLite.
- The app uses a development fallback secret key and has no CSRF protection. Demo credentials and Compose database credentials are for local development only; configure secure secrets and appropriate protections before any real deployment.

## Tests

Install the project dependencies, then run the test suite with:

```bash
python -m pytest
```

The tests cover domain and pricing rules, each use case, web pages, and an end-to-end business scenario. See `docs/traceability.md` for the mapping.
