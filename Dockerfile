FROM python:3.7-alpine as build
RUN apk add build-base cargo git libffi-dev openssl-dev && \
    pip install -U pip && cd / && mkdir wheels && \
    git clone --depth=1 --branch=v1.6.9 https://github.com/syncplay/syncplay.git && \
    echo "" > syncplay/requirements_gui.txt && \
    cd wheels && SNAPCRAFT_PART_BUILD=1 pip wheel file:///syncplay#egg=syncplay

FROM python:3.7-alpine
COPY ./init.sh /syncplay
COPY --from=build /wheels /wheels
RUN apk add --no-cache openssl libffi && pip install /wheels/*.whl
EXPOSE 8999
ENTRYPOINT ["/syncplay"]
