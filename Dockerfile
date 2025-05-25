ARG PYTHON="python:3.12-alpine3.21"
ARG RUNAS="root"

FROM ${PYTHON} AS builder
RUN apk add uv
RUN sh -c '[ $(getconf LONG_BIT) -eq 64 ] || apk add gcc cargo musl-dev libffi-dev openssl-dev'
WORKDIR /build/
RUN --mount=type=bind,ro,source=uv.lock,target=uv.lock \
    --mount=type=bind,ro,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,rw,source=./src/syncplay/,target=./src/syncplay/ \
    uv tree --frozen && \
    uv export --frozen --no-dev --no-emit-package syncplay -o requirements.txt && \
    pip wheel --require-hashes -r requirements.txt --wheel-dir /wheels/ && \
    pip wheel --no-deps ./src/syncplay/ --wheel-dir /wheels/

FROM ${PYTHON} AS root
RUN sh -c '[ $(apk info -e libgcc) ] || apk add --no-cache libgcc'
RUN --mount=type=cache,ro,from=builder,source=/wheels/,target=/wheels/ \
    cd /usr/local/lib/python3.*/ && ls /wheels/*.whl | xargs -P0 -n1 unzip -qd ./site-packages/
COPY ./src/boot.py /usr/bin/syncplay
ENV PYTHONUNBUFFERED=1
EXPOSE 8999
WORKDIR /data/

FROM root AS user
ARG USER_UID=800
ARG USER_GID=800
RUN addgroup -g "${USER_GID}" -S syncplay && \
    adduser -u "${USER_UID}" -S syncplay -G syncplay && \
    chown -R syncplay:syncplay /data
USER syncplay

FROM ${RUNAS}
ENTRYPOINT ["syncplay"]
