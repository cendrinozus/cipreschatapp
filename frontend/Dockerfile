FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM httpd:2.4

COPY --from=builder /app/dist /usr/local/apache2/htdocs/
COPY cipreschatapp.conf /usr/local/apache2/conf/extra/cipreschatapp.conf

RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/ssl/cipreschatapp \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout /etc/ssl/cipreschatapp/cipreschatapp.key \
        -out /etc/ssl/cipreschatapp/cipreschatapp.crt \
        -subj "/CN=chatbot.lacipres.org/O=CIPRES/C=FR" \
    && sed -i 's/^#\(LoadModule ssl_module\)/\1/' /usr/local/apache2/conf/httpd.conf \
    && sed -i 's/^#\(LoadModule socache_shmcb_module\)/\1/' /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule rewrite_module modules/mod_rewrite.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule proxy_module modules/mod_proxy.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule proxy_http_module modules/mod_proxy_http.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "Include conf/extra/cipreschatapp.conf" >> /usr/local/apache2/conf/httpd.conf \
    && sed -i 's/AllowOverride None/AllowOverride All/g' /usr/local/apache2/conf/httpd.conf

EXPOSE 80 443
