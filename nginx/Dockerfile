FROM nginx:1.11.3

RUN rm -f /etc/nginx/conf.d/*
RUN mkdir -p /home/user

ADD nginx.conf /home/user/nginx.conf
ADD uwsgi_params /home/user/uwsgi_params

# Set Timezone
ENV TZ Asia/Tokyo
RUN echo "--- Set timezone" && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

CMD /usr/sbin/nginx -g 'daemon off;' -c /home/user/nginx.conf