ARG PYTHON="python:3.7-alpine3.17"

FROM ${PYTHON} as build
ENV SYNCPLAY="1.6.9"
RUN apk add gcc musl-dev libffi-dev
RUN if [ "$(getconf LONG_BIT)" == "32" ]; then apk add cargo openssl-dev; fi
RUN wget https://github.com/Syncplay/syncplay/archive/refs/tags/v${SYNCPLAY}.tar.gz && \
    tar xf v${SYNCPLAY}.tar.gz
WORKDIR ./syncplay-${SYNCPLAY}/
RUN cat /dev/null > requirements_gui.txt
RUN SNAPCRAFT_PART_BUILD=1 pip wheel --wheel-dir /wheels/ ./
WORKDIR /wheels/
RUN ls *.whl | xargs -P0 -n1 unzip -d /unzip/
WORKDIR /release/local/lib/python3.7/
RUN cp -r /unzip/ ./site-packages/
COPY ./boot.py /release/bin/syncplay

FROM ${PYTHON}
RUN apk add --no-cache libffi openssl
COPY --from=build /release/ /usr/
ENV PYTHONUNBUFFERED=1
EXPOSE 8999
ENTRYPOINT ["syncplay"]
