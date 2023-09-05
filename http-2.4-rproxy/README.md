# Containerised Web Stack

#### 1. Application Stack - Network

We need to make it possible for the tiers in our application stack to be able to communicate. This is typically done with "docker compose", but I'm doing this all within Docker.

I created a Docker network called "app_stack" like this:

	docker network create app_stack

All my images will be run using this network:

	--network=app_stack

#### 2. Presentation Layer - Apache 2.4 Reverse Proxy using SSL Offload

Official Docker httpd Image:
https://hub.docker.com/_/httpd

Extract the configurations from the Docker image for editing:

	docker run --rm httpd:2.4 cat /usr/local/apache2/conf/httpd.conf > my-httpd.conf
	docker run --rm httpd:2.4 cat /usr/local/apache2/conf/extra/httpd-ssl.conf > my-httpd-ssl.conf

Uncomment the following lines in the *my-httpd.conf*:

	LoadModule socache_shmcb_module modules/mod_socache_shmcb.so
	LoadModule ssl_module modules/mod_ssl.so
	LoadModule proxy_module modules/mod_proxy.so
	LoadModule proxy_http_module modules/mod_proxy_http.so
	Include conf/extra/httpd-ssl.conf

If you want to programmatically do this in your Dockerfile:

	RUN sed -i \
			-e 's/^#\(Include .*httpd-ssl.conf\)/\1/' \
			-e 's/^#\(LoadModule .*mod_ssl.so\)/\1/' \
			-e 's/^#\(LoadModule .*mod_socache_shmcb.so\)/\1/' \
			-e 's/^#\(LoadModule .*mod_proxy.so\)/\1/' \
			-e 's/^#\(LoadModule .*mod_proxy_http.so\)/\1/' \
			conf/httpd.conf

Generate your server.key and server.crt for SSL in Apache 2.4:

	openssl genpkey -algorithm RSA -out server.key
	openssl req -new -x509 -key server.key -out server.crt -days 365

I used these inputs for my self-signed certificate:

	Country Name (2 letter code) [AU]:GB
	State or Province Name (full name) [Some-State]:London
	Locality Name (eg, city) []:London
	Organization Name (eg, company) [Internet Widgits Pty Ltd]:My Company
	Organizational Unit Name (eg, section) []:My Org
	Common Name (e.g. server FQDN or YOUR name) []:localhost
	Email Address []:michael@lifecycle-ps.com

To test it before enabling the reverse proxy, you can run this on your host system:

	% curl http://localhost:8080
	<html><head><title>This is a test</title></head><body>This is a test</body></html>%

	% curl -k https://localhost:8443
	<html><head><title>This is a test</title></head><body>This is a test</body></html>%

Create yourself a Dockerfile, mine looks like this:

	FROM  httpd:2.4

	COPY  ./my-httpd.conf  /usr/local/apache2/conf/httpd.conf
	COPY  ./server.crt  /usr/local/apache2/conf/server.crt
	COPY  ./server.key  /usr/local/apache2/conf/server.key
	COPY  ./public-html/index.html  /usr/local/apache2/htdocs/index.html

Note: I created a basic HTML file for testing in, "./public-html/index.html". It's not needed for the reverse proxy but still useful to have. Mine looks like this:

	<html><head><title>This is a test</title></head><body>This is a test</body></html>

When you are ready to build your Presentation layer reverse-proxy Docker image do this:

	docker build -t httpd-2.4-rproxy .

You can run it as a daemon like this:

	docker run -dit --name my-fe -p 8080:80 -p 8443:443 httpd-2.4-rproxy

This will expose TCP 80 on the Docker container as TCP 8080 on the host, and TCP 443 as TCP 8443.

For troubleshooting you may want to run it interactively:

	docker run -it --name my-fe -p 8080:80 -p 8443:443 httpd-2.4-rproxy

The reverse proxy functionality is not running yet, but you should have a working Presentation web server serving a basic HTML page.

To test it, you can run this from your host system:

	% curl http://localhost:8080
	<html><head><title>This is a test</title></head><body>This is a test</body></html>%

	% curl -k https://localhost:8443
	<html><head><title>This is a test</title></head><body>This is a test</body></html>%

To enable the reverse proxy you will need to do the following:

At the end of your *my-httpd.conf* you can add this to forward traffic to your Application tier.

	ProxyPreserveHost On
	ProxyPass / http://my-app/
	ProxyPassReverse / https://my-app/

Note: "my-app" is the name of my Docker app in the Application tier in my example.

You will now want to remove your Docker containers and images and rebuild. I don't have any other Docker containers and images running so I created a script to wipe everything and start over.

	docker container rm -f $(docker container ls | awk {'print $1'} | egrep -v CONTAINER);
	docker image rm -f $(docker image ls | awk {'print $3'} | egrep -v IMAGE);
	docker container prune -f;

WARNING: Do not run these three commands if you have any Docker containers and images you want to keep as it wipes EVERYTHING!

That's an MVP for a reverse proxy in the Presentation layer.

Now if you run the HTTP and HTTPS curl commands above instead of serving the HTML file on the reverse proxy it will forward the request to a container called "my-app" on TCP 80. We have not created this yet so it won't work at the moment.

#### 3. Application Layer - Apache 2.4 Web Server

In order to test the reverse proxy we will need to create our Application tier Docker container. I used the official "httpd" Docker image again which listens on TCP 80.

	cd ./public_html;
	docker run -dit --name my-app --network=app_stack -p 8080:80 -v ./public_html:/usr/local/apache2/htdocs/ httpd:2.4

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


Notes:

docker container rm -f $(docker container ls | grep my-fe | awk {'print $1'} | egrep -v CONTAINER);
docker container prune -f;
docker image rm -f $(docker image ls | grep httpd-2.4-rproxy | awk {'print $3'});
docker container prune -f;
docker build -t httpd-2.4-rproxy .;
docker run -dit --name my-fe --network=app_stack -p 8443:443 httpd-2.4-rproxy; 
docker container exec -it my-fe /bin/bash;