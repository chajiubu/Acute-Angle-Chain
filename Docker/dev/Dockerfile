FROM aacio/builder
ARG branch=master
ARG symbol=SYS

RUN git clone -b $branch https://github.com/AACIO/aac.git --recursive \
    && cd aac && echo "$branch:$(git rev-parse HEAD)" > /etc/aacio-version \
    && cmake -H. -B"/opt/aacio" -GNinja -DCMAKE_BUILD_TYPE=Release -DWASM_ROOT=/opt/wasm -DCMAKE_CXX_COMPILER=clang++ \
       -DCMAKE_C_COMPILER=clang -DCMAKE_INSTALL_PREFIX=/opt/aacio  -DSecp256k1_ROOT_DIR=/usr/local -DBUILD_MONGO_DB_PLUGIN=true -DCORE_SYMBOL_NAME=$symbol \
    && cmake --build /opt/aacio --target install \
    && mv /aac/Docker/config.ini / && mv /opt/aacio/contracts /contracts && mv /aac/Docker/nodaacd.sh /opt/aacio/bin/nodaacd.sh && mv tutorials /tutorials \
    && rm -rf /aac

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install openssl ca-certificates vim psmisc python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip3 install numpy
ENV AACIO_ROOT=/opt/aacio
RUN chmod +x /opt/aacio/bin/nodaacd.sh
ENV LD_LIBRARY_PATH /usr/local/lib
VOLUME /opt/aacio/bin/data-dir
ENV PATH /opt/aacio/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
