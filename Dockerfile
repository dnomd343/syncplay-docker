ARG PYTHON="python:3.12-alpine3.21"

FROM ${PYTHON} AS builder
RUN apk add uv gcc musl-dev libffi-dev
RUN sh -c '[ $(getconf LONG_BIT) -eq 64 ] || apk add cargo openssl-dev'
COPY . /build/
WORKDIR /build/
RUN uv tree --frozen && \
    uv export --frozen --no-emit-package syncplay -o requirements.txt
RUN pip wheel --no-deps ./src/syncplay/ --wheel-dir /wheels/ && \
    pip wheel --require-hashes -r requirements.txt --wheel-dir /wheels/

FROM ${PYTHON}
RUN sh -c '[ $(getconf LONG_BIT) -eq 64 ] || apk add --no-cache libgcc'
RUN --mount=type=cache,ro,from=builder,source=/wheels/,target=/wheels/ \
    cd /usr/local/lib/python3.*/ && ls /wheels/*.whl | xargs -P0 -n1 unzip -d ./site-packages/
COPY ./src/boot.py /usr/bin/syncplay
ENV PYTHONUNBUFFERED=1
EXPOSE 8999
WORKDIR /data/
ENTRYPOINT ["syncplay"]
