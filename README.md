# SaigonBite OFDH prototype (Team 5)

Prototype of the Online Food Delivery Hub platform for the RAD final project (Sem01_2627).
It implements our four main use cases in one running web application.

| Use case | Owner | Where to look |
|---|---|---|
| UC1 Place an order | MOUNTHADY SOUK AKHOM (523K0076) | `app/domain/ordering.py`, `app/controller/ordering.py` |
| UC2 Confirm or reject an incoming order | Dang Doan Minh Tan (523V0017) | `app/domain/kitchen.py`, `app/controller/kitchen.py` |
| UC3 Manage vouchers | MOUNTHADY SOUK AKHOM (523K0076) | `app/domain/vouchers.py`, `app/controller/vouchers.py` |
| UC4 Produce management reports | Dang Doan Minh Tan (523V0017) | `app/domain/reports.py`, `app/controller/reports.py` |

Links for the submission (fill in before Part 2 is handed in):

- GitHub release: _TODO_
- Figma UI: _TODO_
- Demo video: _TODO_

## Run it

You need Python 3.12 or newer. Docker is only needed for PostgreSQL.

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest                                  # run the tests
flask --app app init-db                           # create tables and demo data (SQLite file saigonbite.db)
flask --app app run --debug                       # open http://127.0.0.1:5000
```

With PostgreSQL in Docker (app and database together):

```bash
docker compose up --build                         # open http://localhost:8000
```

To run the app locally against the Docker database only:

```bash
docker compose up -d db
# PowerShell:  $env:DATABASE_URL = "postgresql+psycopg://saigonbite:saigonbite@localhost:5432/saigonbite"
# macOS/Linux: export DATABASE_URL=postgresql+psycopg://saigonbite:saigonbite@localhost:5432/saigonbite
flask --app app init-db
flask --app app run --debug
```

### Demo accounts (password for all: `password`, development only)

| Username | Role | Notes |
|---|---|---|
| `an` | Customer (local) | Vietnamese screens by default; pays by e-wallet, bank QR or cash |
| `tourist` | Customer (tourist) | English screens; pays by international card or cash |
| `kitchen1`, `kitchen2` | Kitchen staff | Hub District 1 and Hub Thu Duc |
| `admin` | Admin | Manages vouchers |
| `manager` | Manager | Reads reports |

Voucher codes in the demo data: `WELCOME10` (10%, minimum 100,000 VND), `SAVE20K` (20,000 VND, minimum 150,000 VND), `OLD5` (expired).

## Layers and folders

```
app/view/         templates, CSS, English and Vietnamese labels      (view)
app/controller/   Flask blueprints: auth, ordering, kitchen, vouchers, reports   (controller)
app/domain/       models.py (persistent classes with business rules), pricing.py,
                  ordering.py, kitchen.py, vouchers.py, reports.py     (domain)
app/data/         database.py, repositories.py, seed.py               (data access)
sql/schema.sql    PostgreSQL tables (generated: python scripts/export_schema.py)
tests/            pytest: rules, one file per use case, and page tests
docs/models/      put PlantUML and diagram sources here
docs/traceability.md   use case to requirement to code to test
```

Rule of the layers: controllers never contain business rules, domain classes never contain SQL, and only
`app/data/repositories.py` runs queries.

## Business rules in the code (from the Assumption Log)

| Rule | Where |
|---|---|
| A-01, A-02 maximum 7 km, fee bands 15,000 / 25,000 / 35,000 VND | `domain/pricing.py` |
| A-03 rain surcharge 10,000 VND when the hub is in rain mode | `domain/pricing.py`, `Hub.rain_mode` |
| A-04 load = Confirmed + Preparing orders / capacity; busy from 80%, no new orders at 100% | `Hub.state`, `OrderingService.quote` |
| A-05 quiet hub (40% or less) gives 5,000 VND off the delivery fee | `domain/pricing.py` |
| A-06, A-07 cancel only while Placed or Confirmed; online payments refunded in full | `Order.cancel`, `Order._release_payment` |
| A-08 payment options by customer type; online payment taken at placement (simulated) | `domain/ordering.py` |
| A-09 out of stock: reject the whole order | `Order.reject`, `KitchenService.reject` |
| A-10 vouchers: percent or fixed on the items only, one per order, one use per customer | `Voucher` |
| A-12, A-20 reports from system data; late means over 45 minutes | `domain/reports.py` |
| A-14 order states and transitions | `models.TRANSITIONS` |
| A-16, A-17 staff see only their own hub; address and phone only in the kitchen view | `KitchenService`, `kitchen.html` |

## Known limits (be honest about these in the report)

- The payment gateway, SMS and maps are simulated (assumption A-18). The customer types the distance from the hub.
- No CSRF protection and a shared development password: do not deploy this as it is.
- Customers, hubs, brands and menu items are created by the seed data only; no use case in our portfolio manages them (assumption A-13, to be confirmed with the lecturer).
- The shipper and office staff roles are not built. The kitchen page has a supporting "next step" button so that orders can reach Delivered or Failed and the reports have data.
- Error messages are in English only; labels on customer pages are English and Vietnamese.
- Tests run on SQLite. The PostgreSQL and Docker set-up follows the same code but must be tried on your own machines.
- Performance targets (NFRs) are not load-tested.

## Using AI-generated code in the course

This code was generated with AI help (Claude). Declare it in the AI Usage Log, read and understand every file you own,
and make your own commits as you adapt it. The design diagrams in report sections II and III must match this code
(or change the code to match your design).
