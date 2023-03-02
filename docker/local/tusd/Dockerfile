# FROM tusproject/tusd:sha-cdc9edb
FROM tusproject/tusd:sha-8889869

USER root

RUN mkdir -p /srv/tusd-data/data && \
    chown -R tusd:tusd /srv/tusd-data/data

USER tusd

ENTRYPOINT [ "tusd" ]
