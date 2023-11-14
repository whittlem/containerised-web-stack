FROM httpd:2.4

COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./my-httpd-ssl.conf /usr/local/apache2/conf/httpd-ssl.conf
COPY ./server.crt /usr/local/apache2/conf/server.crt
COPY ./server.key /usr/local/apache2/conf/server.key
COPY ./public-html /usr/local/apache2/htdocs

RUN DEBIAN_FRONTEND=noninteractive apt update && \
    apt-get install --no-install-recommends -y \
    build-essential iputils-ping net-tools curl apache2-utils && \
    rm -rf /var/lib/apt/lists/*

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
ENV NVM_DIR /root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install 20.9.0 && nvm use 20.9.0

RUN rm -f /usr/local/apache2/htdocs/index.html

ENV PATH="/root/.nvm/versions/node/v20.9.0/bin:${PATH}"
WORKDIR /usr/local/apache2/htdocs
RUN echo "PUBLIC_URL=/" > .env
RUN sed -i 's/"build": "react-scripts build"/"build": "PUBLIC_URL=\/ react-scripts build"/' package.json
RUN npm run build
RUN rm -rf public
RUN cp -r build public