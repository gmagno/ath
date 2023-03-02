FROM python:3.9.16-bullseye

ENV USER_ID=1000
ENV GROUP_ID=1000
ENV USER_NAME=ath

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN groupadd -g ${GROUP_ID} ${USER_NAME}
RUN useradd ${USER_NAME} -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash

COPY --chown=${USER_ID}:${GROUP_ID} ./ath/requirements/local.lock.txt /requirements/

RUN pip install -U pip && \
    pip install -r /requirements/local.lock.txt

COPY --chown=${USER_ID}:${GROUP_ID} ./docker/local/api/entrypoint /entrypoint
COPY --chown=${USER_ID}:${GROUP_ID} ./docker/local/api/start /start
COPY --chown=${USER_ID}:${GROUP_ID} ./docker/local/api/start-test /start-test
COPY --chown=${USER_ID}:${GROUP_ID} ./docker/local/huey/start-worker /start-worker

RUN chmod +x /entrypoint && \
    chmod +x /start && \
    chmod +x /start-test && \
    chmod +x /start-worker

WORKDIR /ath/
USER ${USER_NAME}

ENTRYPOINT [ "/entrypoint" ]
