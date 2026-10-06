FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir "django>=6.1,<6.2" "psycopg[binary]>=3.2,<4"

COPY config ./config
COPY expenses ./expenses
COPY locale ./locale
COPY manage.py main.py ./

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
