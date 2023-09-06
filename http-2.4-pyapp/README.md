# Containerised Web Stack

#### 1. Application Stack - Network

We need to make it possible for the tiers in our application stack to be able to communicate. This is typically done with "docker compose", but I'm doing this all within Docker.

I created a Docker network called "app_stack" like this:

	docker network create app_stack

All my images will be run using this network:

	--network=app_stack

#### 2. Application Layer - Apache 2.4 Python Web App

Official Docker httpd Image:
https://hub.docker.com/_/httpd

Extract the configurations from the Docker image for editing:

	docker run --rm httpd:2.4 cat /usr/local/apache2/conf/httpd.conf > my-httpd.conf

Create yourself a Dockerfile, mine looks like this:

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

TODO: Add Python wsgi config and app

#### 4. Testing it all works!

We now have a web server in our Application tier called "my-app" listening on TCP 80 and optionally exposed on TCP 8080. We actually don't need to expose the port as the Docker containers will use the internal ports.

We have our reverse proxy listening on TCP 8080 for HTTP and TCP 8443 for HTTPS. When it receives a connection it will forward the traffic to "my-app" on the internal TCP 80.

	% curl http://localhost:8080
	<html><head><title>This is a test</title></head><body>This is a test</body></html>%

	% curl -k https://localhost:8443
	<html><head><title>This is a test</title></head><body>This is a test</body></html>%

#### 5. Troubleshooting

It may be useful for you to access your "my-fe" and "my-app" containers.

You can do it as follows:

	docker container exec -it my-fe /bin/bash
	OR
	docker container exec -it my-app /bin/bash

If you want to use any diagnostic tools like "ifconfig", "ping", or "curl", you will need to install them as follows:

	apt update; apt install -y iputils-ping net-tools curl

#### 6. Fast Rebuild and Deploy

docker container rm -f $(docker container ls | grep my-app | awk {'print $1'} | egrep -v CONTAINER);
docker container prune -f;
docker image rm -f $(docker image ls | grep httpd-2.4-pyapp | awk {'print $3'});
docker container prune -f;
docker build -t httpd-2.4-pyapp .;
docker run -dit --name my-app --network=app_stack httpd-2.4-pyapp;
docker container exec -it my-app /bin/bash;