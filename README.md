# MoneyMate

A personal expense tracker. The first version lets you create an account, record purchases by category, set monthly income, and review your spending.

## Run locally

Requires Python 3.12+ and uv.

```sh
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Open `http://127.0.0.1:8000/` and create an account. Each user's data is kept separate.

## Run with Docker

Install and start Docker Desktop, then run:

```sh
docker compose up --build
```

Open `http://127.0.0.1:8000/`. Docker Compose starts the Django app and PostgreSQL; PostgreSQL data is kept in the `postgres_data` volume. This setup is for local development and demos, not public production hosting. The default database password is for local use only.

To move existing local SQLite data into the Docker PostgreSQL database, first make a backup and export the records from the project environment:

```sh
cp db.sqlite3 /private/tmp/money_tracker_db.sqlite3.backup
uv run python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --exclude sessions --output local-data.json
docker compose up --build -d
docker compose exec web python manage.py loaddata local-data.json
```

The export can contain account and finance data. Keep `local-data.json` private and delete it after confirming the migrated records are present. `.gitignore` excludes SQLite files, but the export file should also be kept out of Git.

## Temporary public demo

The `render.yaml` Blueprint creates a separate Django service and PostgreSQL database in Frankfurt. It does not import local SQLite data. Use only fictional demo data; do not upload real financial records. Render's free web service sleeps after 15 minutes without traffic and may take about a minute to wake up. Its free PostgreSQL database expires after 30 days. For persistent data, choose paid hosting and configure backups before inviting users.

## Temporary public demo

The `render.yaml` Blueprint creates a separate Django service and PostgreSQL database in Frankfurt. It does not import local SQLite data. Deploy only fictional demo data; never upload real financial records to this temporary demo. Render's free web service sleeps after 15 minutes without traffic, and its free PostgreSQL database expires after 30 days. The web service may take about a minute to wake up. For persistent data, choose paid hosting and configure backups before inviting users.

## Features

- Sign-up and login.
- Personal expenses with an amount, description, category, and date.
- Custom categories and a starter set of defaults.
- Monthly income and remaining balance after expenses.
- Monthly and year-to-date spending summaries.
- Yearly reports with monthly trends and category breakdowns.
- Current-month income, spending, and remaining balance on the reports page.
- Savings goals with progress tracking and recorded contributions.
- Month-over-month comparisons for total spending and each category.
- One-click access to a confirmation screen before deleting an expense.
- Account-level currency preferences (EUR, USD, GBP, PLN, CHF, CAD, AUD, JPY, INR, and SEK).
- Account-level language preference (English, Russian, Ukrainian, Polish, or German).
- SQLite for local development.

## Database and deployment

The app uses SQLite locally. PostgreSQL is available by setting `DB_ENGINE=postgresql` and providing `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_HOST` (optionally `DB_PORT` and `DB_SSLMODE`). Then apply migrations with `uv run python manage.py migrate`. Changing the backend does not copy existing SQLite data; migrate or export it before switching databases.

Before public deployment, set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS`. Use HTTPS and a PostgreSQL service configured for encrypted connections, encrypted backups, and restricted access. Do not commit database credentials or `.env` files.

Currency is an account-wide display unit. Changing it does not convert values already entered, so keep one currency per account.

## Security notes

Django stores passwords as salted PBKDF2 hashes, and the app scopes expense and income queries to the signed-in account. The local SQLite file and database records are not encrypted by the app itself. FileVault can protect a Mac at rest; a deployed database should use provider-managed encryption, TLS, backups, and restricted network access. The app still needs deployment review before it is ready for real users.
