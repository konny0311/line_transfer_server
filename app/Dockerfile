FROM python:3.8-buster

# 必要なファイルをappディレクトリへコピー
COPY ./ /app

# appディレクトリをルート設定
WORKDIR /app

RUN apt update &&\
    apt install -y redis-server uwsgi-plugin-python3

RUN pip3 install -r requirements.txt

# uwsgiに必要なファイル設定
RUN mkdir /var/log/uwsgi && \
    chown www-data:www-data /var/log/uwsgi

CMD ["uwsgi", "--ini", "uwsgi.ini"]