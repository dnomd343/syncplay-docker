ARG PYTHON="python:3.7-alpine3.17"

FROM ${PYTHON} as build
ENV SYNCPLAY="1.6.9"
RUN apk add gcc musl-dev libffi-dev
RUN wget https://github.com/Syncplay/syncplay/archive/refs/tags/v${SYNCPLAY}.tar.gz && \
    tar xf v${SYNCPLAY}.tar.gz
WORKDIR ./syncplay-${SYNCPLAY}/
RUN cat /dev/null > requirements_gui.txt
RUN SNAPCRAFT_PART_BUILD=1 pip wheel --wheel-dir /wheels/ ./
WORKDIR /wheels/
RUN pip install *.whl
RUN ls *.whl | xargs -P0 -n1 unzip -d /unzip/
WORKDIR /release/lib/python3.7/
RUN cp -r /unzip/ ./site-packages/
WORKDIR /release/bin/
RUN cp /usr/local/bin/syncplay-server ./
COPY ./init.sh ./syncplay

FROM ${PYTHON}
RUN apk add --no-cache libffi openssl
COPY --from=build /release/ /usr/local/
EXPOSE 8999
ENTRYPOINT ["syncplay"]
