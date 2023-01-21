# Install dependencies using multi-stage build
FROM python:3.9.13-bullseye

# Set timezone
RUN apt update; apt -y install tzdata && \
cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

COPY app/. /app
COPY requirements.txt /app
COPY .env /app

WORKDIR /app

RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
