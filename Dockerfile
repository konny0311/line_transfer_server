FROM python:3.8-buster

# 必要なファイルをappディレクトリへコピー
COPY ./ /app

# appディレクトリをルート設定
WORKDIR /app

RUN apt update &&\
    apt install -y redis-server

RUN pip3 install -r requirements.txt

CMD ["python3"]