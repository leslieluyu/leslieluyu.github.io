FROM openresty/openresty:alpine-fat

RUN apk update && apk add --no-cache build-base pcre2-dev openssl-dev

RUN cd /tmp && \
    wget https://openresty.org/download/openresty-1.25.3.1.tar.gz && \
    tar -zxvf openresty-1.25.3.1.tar.gz && \
    cd openresty-1.25.3.1 && \
    ./configure --prefix=/usr/local/openresty \
        --with-http_ssl_module \
        --with-http_v2_module \
        --with-http_v3_module && \
    make -j$(nproc) && \
    make install

# Clean up
RUN apk del build-base pcre2-dev openssl-dev && \
    rm -rf /tmp/openresty-1.25.3.1.tar.gz /tmp/openresty-1.25.3.1

#Verify the modules are included
RUN /usr/local/openresty/bin/openresty -V && ls /usr/local/openresty/nginx/modules/ngx_http_proxy_module.so