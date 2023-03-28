ARG PYTHON="python:3.9-alpine3.17"

FROM ${PYTHON} as build
ENV SYNCPLAY="1.7.0"
RUN apk add gcc musl-dev libffi-dev
RUN if [ "$(getconf LONG_BIT)" == "32" ]; then apk add cargo openssl-dev; fi
RUN wget https://github.com/Syncplay/syncplay/archive/v${SYNCPLAY}.tar.gz -O- | tar xz
WORKDIR ./syncplay-${SYNCPLAY}/
RUN cat /dev/null > requirements_gui.txt
RUN SNAPCRAFT_PART_BUILD=1 pip wheel --wheel-dir /wheels/ ./
WORKDIR /release/local/lib/
RUN mkdir $(basename /usr/local/lib/python3.*/) && cd ./python3.*/ && \
    ls /wheels/*.whl | xargs -P0 -n1 unzip -d ./site-packages/
COPY ./boot.py /release/bin/syncplay

FROM ${PYTHON}
RUN apk add --no-cache libffi openssl
COPY --from=build /release/ /usr/
ENV PYTHONUNBUFFERED=1
EXPOSE 8999
ENTRYPOINT ["syncplay"]
