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

## Features

- Sign-up and login.
- Personal expenses with an amount, description, category, and date.
- Custom categories and a starter set of defaults.
- Monthly income and remaining balance after expenses.
- Monthly and year-to-date spending summaries.
- SQLite for local development.

Before public deployment, set `DJANGO_SECRET_KEY`, turn off `DJANGO_DEBUG`, and configure a production database.
