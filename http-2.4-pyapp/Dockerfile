FROM httpd:2.4

COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./headers_app.wsgi /usr/local/apache2/conf/headers_app.wsgi
COPY ./public-html/index.html /usr/local/apache2/htdocs/index.html

RUN DEBIAN_FRONTEND=noninteractive apt update && \
    apt-get install --no-install-recommends -y \
    build-essential iputils-ping net-tools curl apache2-utils python3 libapache2-mod-wsgi-py3 && \
    rm -rf /var/lib/apt/lists/*

RUN cp /usr/lib/apache2/modules/mod_wsgi.so /usr/local/apache2/modules && \
    chmod 755 /usr/local/apache2/modules/mod_wsgi.so