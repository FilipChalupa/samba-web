FROM alpine:3.20

RUN apk add --no-cache \
    nginx \
    samba-client \
    tini

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN mkdir -p /data /run/nginx

COPY nginx.conf /etc/nginx/http.d/default.conf
COPY sync.sh /sync.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /sync.sh /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/entrypoint.sh"]
