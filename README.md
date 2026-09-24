# Vehicle Parking App — v1

A server-rendered Flask application for booking parking slots. Admins manage lots and spots; users search, book, and release reservations with automatic hourly pricing.

## Features

- **Role-based auth** — admin vs user sessions (Flask session cookies)
- **Parking lots & spots** — CRUD with auto-generated spot maps; delete blocked while occupied
- **Booking flow** — search by location/pincode, book first available spot, release with cost = hours × lot price
- **Admin search** — find users or lots; live available/occupied counts
- **Summary charts** — matplotlib pie (revenue/lot) and bar (occupancy) rendered to static PNGs

## Tech stack

| Layer | Tech |
|-------|------|
| Backend | Flask 3, SQLite (raw `sqlite3`) |
| Templates | Jinja2 |
| Charts | matplotlib |
| Auth | Flask session |

## Setup

```bash
cd vehicle_parking_app_24f2006661
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Environment

Copy the template and set a real secret:

```bash
cp .env.example .env   # or create .env with:
# SECRET_KEY=your-long-random-string
```

`.env` is gitignored. Never commit secrets.

## Run

```bash
python app.py
```

Open http://127.0.0.1:5000 — redirects to `/login`.

## Project layout

```
vehicle_parking_app_24f2006661/
  app.py              # Flask app + all routes
  models/database.py  # schema helpers
  templates/          # Jinja2 pages
  static/             # CSS + generated chart PNGs
  data/parking.db     # SQLite (gitignored)
  .env                # SECRET_KEY (gitignored)
```

## License

For coursework / personal use.
