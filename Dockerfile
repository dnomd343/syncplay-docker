ARG PYTHON="python:3.12-alpine3.22"


FROM ${PYTHON} AS builder
RUN apk add uv binutils && pip install wheel
RUN sh -c '[ $(getconf LONG_BIT) -eq 64 ] || apk add gcc cargo musl-dev libffi-dev openssl-dev'

WORKDIR /build/
COPY uv.lock pyproject.toml ./
RUN uv export --frozen --no-dev --no-emit-package syncplay -o requirements.txt && \
    pip wheel --require-hashes -r requirements.txt --wheel-dir /wheels/

RUN ls /wheels/*.whl | xargs -n1 -P0 wheel unpack -d /wheels/unpack/ && \
    find /wheels/unpack/ -name '*.so' -exec strip {} + && \
    ls -d /wheels/unpack/* | xargs -n1 -P0 wheel pack -d /wheels/

RUN --mount=type=bind,rw,source=./src/syncplay/,target=./src/syncplay/ \
    sed -i '/ep_client/s/ =/-client =/g; s/requirements_gui.txt/\/dev\/null/g' ./src/syncplay/setup.py && \
    pip wheel --no-deps ./src/syncplay/ --wheel-dir /wheels/

RUN --mount=type=bind,rw,source=./src/,target=./src/ \
    uv build --wheel -o /wheels/


FROM ${PYTHON}
LABEL org.opencontainers.image.vendor="Dnomd343"
LABEL org.opencontainers.image.authors="dnomd343@gmail.com"
LABEL org.opencontainers.image.source="https://github.com/dnomd343/syncplay-docker.git"

RUN sh -c '[ $(apk info -e libgcc) ] || [ $(getconf LONG_BIT) -eq 64 ] || apk add --no-cache libgcc'
RUN --mount=type=cache,ro,from=builder,source=/wheels/,target=/wheels/ \
    PYTHONDONTWRITEBYTECODE=1 pip install --no-index --no-compile --no-cache-dir --find-links=/wheels/ /wheels/*.whl

ARG USER_UID=0
ARG USER_GID=0
RUN sh -c '[ $(getent group ${USER_GID}) ] || addgroup -g ${USER_GID} -S syncplay' && \
    sh -c '[ $(getent passwd ${USER_UID}) ] || adduser -u ${USER_UID} -G $(getent group ${USER_GID} | cut -d: -f1) -S syncplay' && \
    rm -rf /etc/group- /etc/passwd- /etc/shadow-
USER ${USER_UID}:${USER_GID}

EXPOSE 8999
WORKDIR /data/
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["syncplay"]
