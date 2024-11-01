FROM python:3.11-slim-buster

WORKDIR /app
COPY . .

RUN pip install -U pip && \
    pip install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5050", "flask-app:app"]
