# Install dependencies using multi-stage build
FROM python:3.9.13-bullseye

# Set timezone
RUN apt update; apt -y install tzdata && \
cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt update
RUN apt -yV upgrade
RUN apt install -y poppler-utils poppler-data
RUN apt install -y libgl1-mesa-dev
RUN apt install -y libreoffice libreoffice-l10n-ja libreoffice-dmaths libreoffice-ogltrans libreoffice-writer2xhtml libreoffice-help-ja
RUN wget https://moji.or.jp/wp-content/ipafont/IPAexfont/IPAexfont00301.zip
RUN unzip IPAexfont00301.zip
RUN mkdir -p /usr/share/fonts/ipa
RUN cp IPAexfont00301/*.ttf /usr/share/fonts/ipa
RUN fc-cache -fv

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
