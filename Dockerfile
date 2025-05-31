ARG PYTHON="python:3.12-alpine3.21"

FROM ${PYTHON} AS builder
RUN apk add uv
RUN sh -c '[ $(getconf LONG_BIT) -eq 64 ] || apk add gcc cargo musl-dev libffi-dev openssl-dev'
WORKDIR /build/
RUN --mount=type=bind,rw,source=./src/,target=./src/ \
    --mount=type=bind,ro,source=uv.lock,target=uv.lock \
    --mount=type=bind,ro,source=pyproject.toml,target=pyproject.toml \
    uv tree --frozen && \
    uv export --frozen --no-dev --no-emit-package syncplay -o requirements.txt && \
    pip wheel --require-hashes -r requirements.txt --wheel-dir /wheels/ && \
    sed -i '/ep_client/s/ =/-client =/g; s/requirements_gui.txt/\/dev\/null/g' ./src/syncplay/setup.py && \
    pip wheel --no-deps ./src/syncplay/ --wheel-dir /wheels/ && \
    uv build --wheel -o /wheels/

FROM ${PYTHON}
RUN sh -c '[ $(apk info -e libgcc) ] || apk add --no-cache libgcc'
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
