FROM minio/minio:latest

RUN mkdir -p /root/.mc
RUN curl https://dl.min.io/client/mc/release/linux-amd64/mc --output /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc
