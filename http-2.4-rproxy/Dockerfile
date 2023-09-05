FROM httpd:2.4

COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./server.crt /usr/local/apache2/conf/server.crt
COPY ./server.key /usr/local/apache2/conf/server.key
COPY ./public-html/index.html /usr/local/apache2/htdocs/index.html

RUN DEBIAN_FRONTEND=noninteractive apt update && \
    apt-get install --no-install-recommends -y \
    build-essential iputils-ping net-tools curl apache2-utils && \
    rm -rf /var/lib/apt/lists/*

RUN htpasswd -b -c /usr/local/apache2/conf/.htpasswd user1 pass1