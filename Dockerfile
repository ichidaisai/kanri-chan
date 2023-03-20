# Install dependencies using multi-stage build
FROM python:3.9.13-bullseye

# Set timezone
RUN apt update; apt -y install tzdata && \
cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt update; apt install -y poppler-utils poppler-data

COPY app/. /app
COPY requirements.txt /app
COPY .env /app
COPY settings.yaml /app
COPY client_secrets.json /app
COPY credentials.json /app

WORKDIR /app

RUN pip install -U pip
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
