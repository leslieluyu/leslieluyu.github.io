FROM nginx:1.25.1

RUN apt-get update \
  && apt-get install -y lua5.1 liblua5.1-0-dev wget tar make \
  && rm -rf /var/lib/apt/lists/*

RUN wget https://openresty.org/download/nginx-1.25.1.tar.gz
RUN tar -xzvf nginx-1.25.1.tar.gz

WORKDIR /nginx-1.25.1

# Export Luajit paths
ENV LUAJIT_LIB=/usr/local/lib 
ENV LUAJIT_INC=/usr/local/include/luajit-2.1

RUN ./configure --prefix=/opt/nginx \
  --with-ld-opt="-Wl,-rpath,/usr/local/lib" \ 
  --add-module=/usr/local/nginx-modules/ngx_devel_kit \
  --add-module=/usr/local/nginx-modules/lua-nginx-module
   
RUN make -j2
RUN make install

# Install lua-resty packages
WORKDIR /usr/local/lua-nginx/lua-resty-core  
RUN make install PREFIX=/opt/nginx
   
WORKDIR /usr/local/lua-nginx/lua-resty-lrucache
RUN make install PREFIX=/opt/nginx

# Add lua package path
RUN echo "lua_package_path "/opt/nginx/lualib/?.lua;;";" >> /opt/nginx/conf/nginx.conf
