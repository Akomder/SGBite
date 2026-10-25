FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# create tables and sample data (only when the database is empty), then start the web server
CMD ["sh", "-c", "flask --app app init-db && gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app"]
