## Quick Start

[简体中文](./docs/README_zh-Hans.md) | [繁體中文](./docs/README_zh-Hant.md) | [日本語](./docs/README_ja.md)

Using a single command to start the [Syncplay](https://syncplay.pl/) service. Yes, that's all it takes.

```bash
$ docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.5
```

> Pressing `Ctrl+C` will terminate the service.

<details>

<summary><b>Unable to access Docker Hub?</b></summary>

<br/>

If you cannot access the Internet, you need to obtain an OCI image and copy it onto a storage medium. For details, see [offline usage](#Registry).

If you are located in China mainland which cannot access Docker Hub normally, you can replace `dnomd343/syncplay` with `ccr.ccs.tencentyun.com/dnomd343/syncplay` , which will use the TCR service in Guangzhou.

---

</details>

If there are no accidents, you can enter the server IP address or domain name on the client for verification, the default port is `tcp/8999` . If you are unable to connect, please check your firewall settings.

To run the service in the background, you can use the following command to start Syncplay:

```bash
$ docker run -d --net=host \
    --restart=always --name=syncplay dnomd343/syncplay
```

> You can use `docker ps -a` to see the running containers, and use `docker rm -f syncplay` to stop the service.

You can add more arguments to customize the service. For example, you can require a password when connecting to the server, disable chat, and display a welcome message upon entering the room. You can use the following commands:

> Note that before pressing Enter, you must execute `docker rm -f syncplay` to remove the existing service, otherwise they will conflict.

```bash
$ docker run -d --net=host \
    --restart=always --name=syncplay dnomd343/syncplay \
    --disable-chat --motd='Hello' --password='PASSWD'
```

Sometimes, we need to restart the server, it is necessary to persist Syncplay at this time, which means that the room data will be saved to disk. You need to choose a working directory to save them, such as `/etc/syncplay/` , execute the following command, the data will be saved to the `rooms.db` file under working directory.

```bash
$ docker run -d --net=host         \
    --volume /etc/syncplay/:/data/ \
    --restart=always --name=syncplay dnomd343/syncplay \
    --persistent --motd='Persistent Server'
```

This directory can be used for additional purposes. For example, adding the `--enable-stats` option will enable statistics, and the data will be saved to a `stats.db` file in the directory. You can also create a `config.yml` file in the directory and write the configuration options in it. Syncplay will automatically read this file at startup, so you don't need to enter a large number of arguments on the command line.

```yaml
# /etc/syncplay/config.yml
password: 'My Password'
persistent: true
enable-stats: true
disable-chat: false
motd: |
  Hello, here is a syncplay server.
  More information...
```

When deploying, it's always a good idea to enable TLS (although this step is optional and can be skipped), and fortunately, Syncplay makes it easy to do so. Before starting, you need to prepare a domain name and point its DNS to your current server. Additionally, you must have the domain's private key and certificate files.

You can obtain a certificate through [`acme.sh`](https://acme.sh/) , [`certbot`](https://certbot.eff.org/), or other suitable methods. Anyway, you will end up with a private key and certificate file, and Syncplay requires you to provide the following three files:

> Some CAs may not provide chain file, you need to obtain them manually, such as [`whatsmychaincert`](https://whatsmychaincert.com/) .

+ `cert.pem` : The certificate issued by the CA.
+ `chain.pem` : The CA certificate chain.
+ `privkey.pem` : The private key of the certificate.

For example, with `acme.sh` , you can execute a command like the following to save the private key and certificate files for the domain name `343.re` to the `/etc/ssl/certs/343.re/` directory.

```bash
$ acme.sh --install-cert -d 343.re               \
    --cert-file  /etc/ssl/certs/343.re/cert.pem  \
    --ca-file    /etc/ssl/certs/343.re/chain.pem \
    --key-file   /etc/ssl/certs/343.re/privkey.pem
```

Now that everything is ready, you just need to execute the following command. This will start a more secure and private Syncplay service.

```bash
$ docker run -d --net=host                  \
    --volume /etc/syncplay/:/data/          \
    --volume /etc/ssl/certs/343.re/:/certs/ \
    --restart=always --name=syncplay dnomd343/syncplay \
    --enable-tls --motd='Secure Server'
```

> Note that the server address entered by the client must match the certificate, otherwise the connection will fail.

Unlike some services, Syncplay does not need to be manually restarted when the certificate is updated, it will automatically detect certificate changes and use the latest version. In addition, TLS on the Syncplay server is adaptive, which means that even older versions of clients that do not support TLS can still communicate normally, but note that security encryption will not be effective at this time.

## Command-line Arguments

You can customize the Syncplay server by specifying the following command line arguments.

> The following parameters are optimized for Docker and some differences with [official documentation](https://man.archlinux.org/man/extra/syncplay/syncplay-server.1). Please refer to the current document when using.

+ `--config [FILE]` : Specify the configuration file, the default is `config.yml` .

+ `--port [PORT]` : Listening port of Syncplay service, the default is `8999` .

+ `--password [PASSWD]` : Authentication when connecting to the server, not enabled by default.

+ `--motd [MESSAGE]` : The welcome text after the user enters the room, not enabled by default.

+ `--salt [TEXT]` : Specify a random string as the [salt value](https://en.wikipedia.org/wiki/Salt_(cryptography)) used to secure password, defaults to empty.

+ `--random-salt` : Using randomly generated salt value, valid when `--salt` is not specified, not enabled by default.

+ `--isolate-rooms` : Enable room isolation, users cannot see information from anyone outside their room, not enabled by default.

+ `--disable-chat` : Disable the chat feature, not enabled by default.

+ `--disable-ready` : Disable the readiness indicator feature, not enabled by default.

+ `--enable-stats` : Enable the server statistics feature, the data will be saved in the `stats.db` file, not enabled by default.

+ `--enable-tls` : Enable TLS support, the files need to be mounted in the `/certs/` directory, including `cert.pem` , `chain.pem` and `privkey.pem` , not enabled by default.

+ `--persistent` : Enable room data persistence, the information will be saved to the `rooms.db` file, only valid when `--isolate-rooms` is not specified, not enabled by default.

+ `--max-username [NUM]` : Maximum length of usernames, default is `16` .

+ `--max-chat-message [NUM]` : Maximum length of chat messages, default is `150` .

+ `--permanent-rooms [ROOM ...]` : Specifies a list of rooms that will still be listed even if their playlist is empty, only valid when `--persistent` is specified, defaults to empty.

+ `--listen-ipv4 [ADDR]` : Listening address of Syncplay service on IPv4 network, not enabled by default.

+ `--listen-ipv6 [ADDR]` : Listening address of Syncplay service on IPv6 network, not enabled by default.

> When you specify only `--listen-ipv4` , Syncplay will not listen on IPv6 and vice versa. If both options are provided, Syncplay will operate in dual-stack networking.

Use the `--version` option to display the Syncplay and Python versions, as well as the CPU architecture.

```bash
$ docker run --rm dnomd343/syncplay --version
Syncplay Docker Bootstrap v1.7.5 (Yoitsu 117) [CPython 3.12.13 aarch64]
```

You can also use the following command to output help information.

<details>

<summary><b>Help message of command-line</b></summary>

<br/>

```bash
$ docker run --rm dnomd343/syncplay --help
usage: syncplay [-h] [-v] [-c FILE] [-p PORT] [-k PASSWD] [-m MESSAGE]
                [--salt TEXT] [--random-salt] [--isolate-rooms]
                [--disable-chat] [--disable-ready] [--enable-stats]
                [--enable-tls] [--persistent] [--max-username NUM]
                [--max-chat-message NUM] [--permanent-rooms [ROOM ...]]
                [--listen-ipv4 ADDR] [--listen-ipv6 ADDR]

Syncplay Docker Bootstrap

options:
  -h, --help            Show this help message and exit.
  -v, --version         Show version information and exit.
  -c FILE, --config FILE
                        Specify the configuration file path, the default is
                        `config.yml`.
  -p PORT, --port PORT  Listening port of Syncplay service, the default is
                        8999.
  -k PASSWD, --password PASSWD
                        Authentication when connecting to the server.
  -m MESSAGE, --motd MESSAGE
                        The welcome text after the user enters the room.
  --salt TEXT           A string used to secure passwords, defaults to empty.
  --random-salt         Use a randomly generated salt value, valid when
                        `--salt` is not specified.
  --isolate-rooms       Enable room isolation, users cannot see information
                        from anyone outside their room.
  --disable-chat        Disables the chat feature.
  --disable-ready       Disables the readiness indicator feature.
  --enable-stats        Enable the server statistics feature, the data will be
                        saved in the `stats.db` file.
  --enable-tls          Enable TLS support, the private key and certificate
                        needs to be mounted in the `/certs/` directory.
  --persistent          Enable room data persistence, the information will be
                        saved to the `rooms.db` file, only valid when
                        `--isolate-rooms` is not specified.
  --max-username NUM    Maximum length of usernames, default is 16.
  --max-chat-message NUM
                        Maximum length of chat messages, default is 150.
  --permanent-rooms [ROOM ...]
                        Specifies a list of rooms that will still be listed
                        even if their playlist is empty, only valid when
                        `--persistent` is specified, defaults to empty.
  --listen-ipv4 ADDR    Listening address of Syncplay service on IPv4.
  --listen-ipv6 ADDR    Listening address of Syncplay service on IPv6.
```

</details>

## Configure File

If you need to configure many options, entering a large number of command-line arguments each time you start can be troublesome and error-prone. Instead, you can write them into a configuration file.

By creating a `config.yml` file in the working directory, you can use the YAML format to specify any arguments that are supported on the command line. Syncplay will automatically read and load this file on startup. However, please note that if the same arguments are specified both of them, the command-line arguments will override those in the configuration file.

```yaml
port: 7999
salt: 'SALT'
random-salt: true
password: 'My Password'
persistent: true
enable-tls: true
enable-stats: true
isolate-rooms: true
disable-chat: true
disable-ready: true
max-username: 256
max-chat-message: 2048
listen-ipv4: 127.0.0.1
listen-ipv6: ::1
permanent-rooms:
  - ROOM_1
  - ROOM_2
  - ROOM_3
motd: |
  Hello, here is a syncplay server.
  More information...
```

You can also use JSON or TOML formats for the configuration file, which is identified by the file suffix. By default, the configuration file is named `config.yml` , but you can specify a different file by using the `--config` parameter or passing the `CONFIG` environment variable.

## Environment Variables

The Syncplay container also supports configuration via environment variables. Only three types of fields are supported: numbers, strings, and booleans. Environment variable names should be in uppercase letters, with `-` replaced by `_` , boolean values are represented by `ON` or `TRUE`. Below is an example of how to use environment variables for configuration.

```bash
$ docker run -d --net=host \
    --env PORT=7999        \
    --env MOTD=Hello       \
    --env DISABLE_CHAT=ON  \
    --restart=always --name=syncplay dnomd343/syncplay
```

As you may have noticed, there are three ways to configure Syncplay: command-line arguments, configuration file, and environment variables. Their priority is from high to low, that is, the command-line arguments will override the options of the configuration file, and the configuration file will override the environment variables. You can combine them as needed.

## Docker Compose

Using `docker compose` to deploy Syncplay is a more elegant way. You need to create a `docker-compose.yml` configuration file and write the following example.

```yaml
# /etc/syncplay/docker-compose.yml
services:
  syncplay:
    container_name: syncplay
    image: dnomd343/syncplay
    network_mode: host
    restart: always
    volumes:
      - ./:/data/
      - /etc/ssl/certs/343.re/:/certs/  # only when enable TLS
```

We save this file in the `/etc/syncplay/` aka working directory. Since a relative path in `volumes` option is used, it is also in the working directory. Execute the following command in this directory to start the Syncplay service.

```bash
$ docker compose up -d
[+] Running 1/1
✔ Container syncplay Started
```

> Adding the `-d` option allows the service to run in the background.

Similarly, you can map the certificate directory to enable TLS functionality, and edit the `config.yml` file to configure additional options.

## Security

In the commands above, we use `--net=host` to expose external services, which allows the container to access the host network directly. However, from a security perspective, it is recommended to use the `bridge` network and map the `tcp/8999` port, even though this may result in a slight performance decrease.

```bash
$ docker run -d -p 8999:8999 \
    --restart=always --name=syncplay dnomd343/syncplay
```

By default, Docker runs containers as the root user, which can pose a security risk. The images built by this project comply with the OCI standard, so you can use [Podman](https://podman.io/) as a complete replacement for Docker, which runs in non-root mode by default.

```bash
$ podman run -d -p 8999:8999 \
    --restart=always --name=syncplay dnomd343/syncplay
```

Alternatively, you can use Docker [rootless mode](https://docs.docker.com/engine/security/rootless/), although it is quite cumbersome to configure. If you only want to use Docker, you can specify the `UID` and `GID` when building the image so that the container will not have root permissions.

```bash
# Check the current non-root UID and GID values.
$ id
uid=1000(dnomd343) gid=1000(dnomd343) ...

# Use these obtained UID and GID values as build arguments.
$ docker build -t my-syncplay \
    --build-arg USER_UID=1000 \
    --build-arg USER_GID=1000 \
    https://github.com/dnomd343/syncplay-docker.git

$ docker run -d -p 8999:8999 \
    --restart=always --name=syncplay my-syncplay
```

## Registry

The images released by this project comply with the [OCI Image Format Specification](https://github.com/opencontainers/image-spec) and can be distributed on any registry that supports the [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec). In the current workflow, GitHub Actions will automatically distribute the images to the following registries:

- Docker Hub: `dnomd343/syncplay`
- Github Package: `ghcr.io/dnomd343/syncplay`
- Tencent Cloud: `ccr.ccs.tencentyun.com/dnomd343/syncplay`

There are four CPU architectures are supported: `amd64` , `arm64` , `i386` and `arm/v7` . When you pull an image, the container tool will automatically select the appropriate version based on your host architecture.

You can pull the original OCI image and save it as a tar file for offline use. It is recommended to use the [skopeo](https://github.com/containers/skopeo.git) tool for this purpose.

> You can also use the `docker save` command to export the image, but only supports a single architecture.

```bash
# Archive images of all architectures for 1.7.5 version.
$ skopeo copy --all                             \
    docker://docker.io/dnomd343/syncplay:v1.7.5 \
    oci-archive:syncplay-v1.7.5.tar

# Archive image of `arm64` architecture for 1.7.5 version.
$ skopeo copy --override-os=linux --override-arch=arm64 \
    docker://docker.io/dnomd343/syncplay:v1.7.5         \
    oci-archive:syncplay-v1.7.5-arm64.tar

# Move to another computer and extract for docker.
$ docker load < syncplay-v1.7.5.tar
```

## Troubleshooting

If you encounter any errors, please first use the `docker logs syncplay` command to view the process output, as it may contain useful error information. You can also enable more detailed logs by setting the environment variable `DEBUG=ON` .

```bash
$ docker run --rm --env DEBUG=ON dnomd343/syncplay
ENV_OPTS -> ...
CFG_OPTS -> ...
ARG_OPTS -> ...
Environment variables -> ...
Configure content -> ...
Environment options -> ...
Command line options -> ...
Configure file options -> ...
Bootstrap final options -> {}
Syncplay startup arguments -> ['syncplay', '--port', '8999', '--salt', '']
Welcome to Syncplay server, ver. 1.7.5
```

## Advanced

For some reasons, you may need to change the path of the configuration files or working directory. This is possible in the Syncplay container, which requires you to specify it using environment variables.

+ `TEMP_DIR` ：The temporary directory, which does not need to be persisted, defaults to `/tmp/` .

+ `WORK_DIR` ：The working directory, which stores data related to Syncplay, defaults to `/data/` .

+ `CERT_DIR` ：The certificate directory, used to store TLS certificates and private key files, defaults to `/certs/` .

## Build Image

> This project utilizes several [BuildKit](https://github.com/moby/buildkit.git) features during its build (bundled after Docker 23.0) . As a result, other build tools may experience compatibility issues.

You can build an image directly from the source code using the following command.

```bash
$ docker build -t syncplay https://github.com/dnomd343/syncplay-docker.git
```

You may also modify the source code to implement your own customizations.

```bash
$ git clone https://github.com/dnomd343/syncplay-docker.git

$ cd ./syncplay-docker/
# some edit...

$ docker build -t syncplay .
```

If you require images for multiple architectures, you should use the `buildx` command to build them.

```bash
$ docker buildx build -t dnomd343/syncplay                    \
    --platform=linux/amd64,linux/386,linux/arm64,linux/arm/v7 \
    https://github.com/dnomd343/syncplay-docker.git --push
```

## License

MIT License ©2026 [@dnomd343](https://github.com/dnomd343)
