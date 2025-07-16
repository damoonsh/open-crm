# Use a slim Python base image
FROM python:3.10-slim-buster

RUN apt-get update -qq && \
    apt-get install -y -qq postgresql-client > /dev/null 2>&1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --quiet --no-cache-dir -r requirements.txt

COPY . /app/

RUN alembic init app/migrations

RUN chmod +x /app/a.sh
EXPOSE 8000
ENTRYPOINT ["/app/a.sh"]