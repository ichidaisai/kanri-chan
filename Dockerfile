# Install dependencies using multi-stage build
FROM python:3.9.13-bullseye

# Set timezone
RUN apt update; apt -y install tzdata && \
cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt update; apt install -y poppler-utils poppler-data libgl1-mesa-dev

RUN pip install -U pip==23.0.1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/. .
COPY .env .
COPY settings.yaml .
COPY client_secrets.json .
COPY credentials.json .

CMD ["python", "main.py"]
