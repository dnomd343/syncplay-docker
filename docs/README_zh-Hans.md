## 快速开始

仅需一行命令开启 [Syncplay](https://syncplay.pl/) 服务，是的，就这么简单。

```bash
$ docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.5
```

> 按下 `Ctrl+C` 可终止服务。

<details>

<summary><b>无法访问 Docker Hub？</b></summary>

<br/>

如果无法访问 Internet，需要先获取 OCI 镜像并复制到存储介质。详情请参见 [offline usage](#Registry) 。

如果您位于中国大陆且无法正常访问 Docker Hub，可将 `dnomd343/syncplay` 替换为 `ccr.ccs.tencentyun.com/dnomd343/syncplay`，这将使用广州的 TCR 服务。

---

</details>

如果没有意外，可在客户端填写服务器 IP 或域名进行验证，默认端口为 `tcp/8999` 。如果您无法连接，请检查防火墙设置。

若要在后台运行服务，请使用下面的命令启动 Syncplay ：

```bash
$ docker run -d --net=host \
    --restart=always --name=syncplay dnomd343/syncplay
```

> 使用 `docker ps -a` 可查看正在运行的容器，使用 `docker rm -f syncplay` 可停止服务。

您可以通过附加参数定制服务，例如要求连接时输入密码、禁用聊天，并在进入房间时显示欢迎语。示例如下：

> 注意：按回车前请先执行 `docker rm -f syncplay` 移除已存在服务，否则会发生冲突。

```bash
$ docker run -d --net=host \
    --restart=always --name=syncplay dnomd343/syncplay \
    --disable-chat --motd='Hello' --password='PASSWD'
```

有时需要重启服务器，此时有必要将 Syncplay 持久化保存，也就是把房间数据写入磁盘。您可以指定一个工作目录，比如 `/etc/syncplay/`，执行下面命令后，数据会保存到该目录下的 `rooms.db` 文件。

```bash
$ docker run -d --net=host         \
    --volume /etc/syncplay/:/data/ \
    --restart=always --name=syncplay dnomd343/syncplay \
    --persistent --motd='Persistent Server'
```

该目录还可用于其他用途。例如添加 `--enable-stats` 选项将启用统计功能，数据会保存到目录下的 `stats.db` 文件。您还可以在该目录中创建 `config.yml` 文件，将配置选项写入其中。Syncplay 启动时会自动读取此文件，无需在命令行中输入大量参数。

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

部署时启用 TLS 通常是个好主意（本步骤可选），幸运的是 Syncplay 可以很简单地做到这点。在开始前，您需要准备域名并将其 DNS 指向当前服务器，同时准备域名的私钥和证书文件。

证书可通过 [`acme.sh`](https://acme.sh/) 、[`certbot`](https://certbot.eff.org/) 或其他方式获取。最终您会得到私钥和证书文件，Syncplay 需要以下三个文件：

> 某些 CA 可能不会提供 chain 文件，需要您手动获取，例如 [`whatsmychaincert`](https://whatsmychaincert.com/) 。

+ `cert.pem`：CA 签发的证书
+ `chain.pem`：CA 证书链
+ `privkey.pem`：证书私钥

例如使用 `acme.sh` 执行下面命令，将域名 `343.re` 的证书保存到 `/etc/ssl/certs/343.re/` 目录：

```bash
$ acme.sh --install-cert -d 343.re               \
    --cert-file  /etc/ssl/certs/343.re/cert.pem  \
    --ca-file    /etc/ssl/certs/343.re/chain.pem \
    --key-file   /etc/ssl/certs/343.re/privkey.pem
```

准备就绪后，执行以下命令即可启动一个更安全、更私密的 Syncplay 服务：

```bash
$ docker run -d --net=host                  \
    --volume /etc/syncplay/:/data/          \
    --volume /etc/ssl/certs/343.re/:/certs/ \
    --restart=always --name=syncplay dnomd343/syncplay \
    --enable-tls --motd='Secure Server'
```

> 注意客户端输入的服务器地址必须与证书匹配，否则连接会失败。

与一些服务不同，Syncplay 的证书更新后无需手动重启，它会自动检测证书变化并使用最新版本。此外，Syncplay 服务端的 TLS 具有自适应能力，即使旧版本客户端不支持 TLS 仍可正常通信，但此时安全加密将无法生效。

## 命令行参数

通过指定以下命令行参数来定制 Syncplay 服务器：

> 以下参数已针对 Docker 优化，与[官方文档](https://man.archlinux.org/man/extra/syncplay/syncplay-server.1)存在一定差异，使用时请以本说明为准。

+ `--config [FILE]` ：指定配置文件，默认是 `config.yml` 。

+ `--port [PORT]` ：Syncplay 服务监听端口，默认是 `8999` 。

+ `--password [PASSWD]` ：连接服务器的身份验证密码，默认不启用。

+ `--motd [MESSAGE]` ：用户进入房间时显示的欢迎文本，默认不启用。

+ `--salt [TEXT]` ：用于加固密码的随机字符串盐值，默认是空字符串。

+ `--random-salt` ：使用随机生成的盐值，仅在未指定 `--salt` 时生效，默认不启用。

+ `--isolate-rooms` ：启用房间隔离，用户无法看到其他房间的信息，默认不启用。

+ `--disable-chat` ：禁用聊天功能，默认不启用。

+ `--disable-ready` ：禁用就绪指示器功能，默认不启用。

+ `--enable-stats` ：启用服务器统计功能，数据将保存到 `stats.db` ，默认不启用。

+ `--enable-tls` ：启用 TLS 支持，需将证书文件挂载到 `/certs/` 目录，包括 `cert.pem` 、`chain.pem` 和 `privkey.pem` ，默认不启用。

+ `--persistent` ：启用房间数据持久化，信息将保存到 `rooms.db` ，仅在未指定 `--isolate-rooms` 时有效，默认不启用。

+ `--max-username [NUM]` ：用户名最大长度，默认是 `16` 。

+ `--max-chat-message [NUM]` ：聊天消息最大长度，默认是 `150` 。

+ `--permanent-rooms [ROOM ...]` ：指定即使播放列表为空也仍会列出的房间，仅在指定 `--persistent` 时有效，默认为空。

+ `--listen-ipv4 [ADDR]` ：在 IPv4 网络上监听的地址，默认不启用。

+ `--listen-ipv6 [ADDR]` ：在 IPv6 网络上监听的地址，默认不启用。

+ `--version` ：显示 Syncplay 和 Python 版本，以及 CPU 架构。

> 仅指定 `--listen-ipv4` 时，Syncplay 不会在 IPv6 上监听；仅指定 `--listen-ipv6` 时，Syncplay 不会在 IPv4 上监听。若两者均指定，则启用双栈网络。

使用 `--version` 选项显示 Syncplay 和 Python 的版本，同时输出 CPU 架构：

```bash
$ docker run --rm dnomd343/syncplay --version
Syncplay Docker Bootstrap v1.7.5 (Yoitsu 117) [CPython 3.12.13 aarch64]
```

您可以运行下面命令查看帮助信息：

<details>

<summary><b>命令行帮助信息</b></summary>

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
  -h, --help            show this help message and exit.
  -v, --version         show version information and exit.
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

## 配置文件

如果需要配置大量选项，每次启动时输入大量命令行参数会很麻烦且容易出错。此时可以将它们写入配置文件。

在工作目录中创建 `config.yml` 文件，使用 YAML 格式指定命令行支持的所有参数。Syncplay 启动时会自动读取该文件。但是请注意，如果同一参数同时出现在命令行和配置文件中，命令行参数会覆盖配置文件中的值。

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

您还可以使用 JSON 或 TOML 格式的配置文件，Syncplay 会根据文件后缀自动识别。默认配置文件名为 `config.yml` ，也可以通过 `--config` 参数或 `CONFIG` 环境变量指定其他文件。

## 环境变量

Syncplay 容器还支持通过环境变量配置。仅支持数字、字符串和布尔类型三种字段。环境变量名应全部使用大写，并把 `-` 替换为 `_`，布尔值使用 `ON` 或 `TRUE` 表示，下面是一个示例：

```bash
$ docker run -d --net=host \
    --env PORT=7999        \
    --env MOTD=Hello       \
    --env DISABLE_CHAT=ON  \
    --restart=always --name=syncplay dnomd343/syncplay
```

如您所见，Syncplay 支持三种配置方式：命令行参数、配置文件和环境变量。优先级从高到低，也就是命令行参数将覆盖配置文件选项，配置文件将覆盖环境变量，您可根据需要组合使用。

## Docker Compose

使用 `docker compose` 部署 Syncplay 更加优雅。您需要创建一个 `docker-compose.yml` 文件，内容示例如下：

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

将该文件保存在 `/etc/syncplay/` 也就是工作目录下，由于 `volumes` 中使用了相对路径，它也位于工作目录中。进入该目录后执行以下命令即可启动 Syncplay 服务：

```bash
$ docker compose up -d
[+] Running 1/1
✔ Container syncplay Started
```

> 添加 `-d` 参数可让服务在后台运行。

同样，您可以映射证书目录以启用 TLS，并编辑 `config.yml` 配置更多选项。

## 安全

上述命令中我们使用 `--net=host` 直接将容器接入主机网络，会暴露外部服务。出于安全考虑，建议使用 `bridge` 网络并映射 `tcp/8999` 端口，尽管性能可能会略微下降。

```bash
$ docker run -d -p 8999:8999 \
    --restart=always --name=syncplay dnomd343/syncplay
```

默认情况下，Docker 以 root 用户运行容器，这存在安全风险。本项目构建的镜像符合 OCI 标准，因此您可以使用 [Podman](https://podman.io/) 完全替代 Docker，Podman 默认以非 root 模式运行。

```bash
$ podman run -d -p 8999:8999 \
    --restart=always --name=syncplay dnomd343/syncplay
```

或者，您也可以使用 Docker [rootless mode](https://docs.docker.com/engine/security/rootless/)，不过配置较为繁琐。如果只希望继续使用 Docker，可在构建镜像时指定 `UID` 和 `GID` ，使容器不再以 root 权限运行。

```bash
# 检查当前非 root 的 UID 和 GID。
$ id
uid=1000(dnomd343) gid=1000(dnomd343) ...

# 使用获得的 UID 和 GID 作为构建参数。
$ docker build -t my-syncplay \
    --build-arg USER_UID=1000 \
    --build-arg USER_GID=1000 \
    https://github.com/dnomd343/syncplay-docker.git

$ docker run -d -p 8999:8999 \
    --restart=always --name=syncplay my-syncplay
```

## Registry

本项目发布的镜像遵循 [OCI 镜像格式规范](https://github.com/opencontainers/image-spec)，可分发到任何支持 [OCI Distribution 规范](https://github.com/opencontainers/distribution-spec) 的镜像仓库。当前工作流中，GitHub Actions 会自动将镜像分发到以下仓库：

- Docker Hub: `dnomd343/syncplay`
- Github Package: `ghcr.io/dnomd343/syncplay`
- Tencent Cloud: `ccr.ccs.tencentyun.com/dnomd343/syncplay`

当前支持四种 CPU 架构：`amd64`、`arm64`、`i386` 和 `arm/v7` 。在拉取镜像时，容器工具会根据主机架构自动选择合适版本。

您可以将原始 OCI 镜像拉取后导出为 tar 文件以便离线使用。推荐使用 [skopeo](https://github.com/containers/skopeo.git) 工具达成。

> 您也可使用 `docker save` 导出镜像，但仅支持单一架构。

```bash
# 归档 1.7.5 版本所有架构的镜像。
$ skopeo copy --all                             \
    docker://docker.io/dnomd343/syncplay:v1.7.5 \
    oci-archive:syncplay-v1.7.5.tar

# 归档 1.7.5 版本 arm64 架构的镜像。
$ skopeo copy --override-os=linux --override-arch=arm64 \
    docker://docker.io/dnomd343/syncplay:v1.7.5         \
    oci-archive:syncplay-v1.7.5-arm64.tar

# 将镜像移到另一台计算机并在 docker 中解压。
$ docker load < syncplay-v1.7.5.tar
```

## 故障排查

如果遇到错误，请先使用 `docker logs syncplay` 查看进程输出，它通常会提供有用的信息。您也可以通过设置环境变量 `DEBUG=ON` 输出更详细日志。

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

## 高级

由于某些原因，您可能需要更改配置文件路径或工作目录，Syncplay 容器支持通过环境变量指定。

+ `TEMP_DIR` ：临时目录，无需持久化，默认为 `/tmp/` 。
+ `WORK_DIR` ：工作目录，用于存储 Syncplay 相关数据，默认为 `/data/` 。
+ `CERT_DIR` ：证书目录，用于存放 TLS 证书和私钥文件，默认为 `/certs/` 。

## 构建镜像

> 本项目在构建过程中使用了若干 [BuildKit](https://github.com/moby/buildkit.git) 特性（随 Docker 23.0 及更高版本捆绑）。因此其他构建工具可能会出现兼容性问题。

您可以直接从源码构建镜像：

```bash
$ docker build -t syncplay https://github.com/dnomd343/syncplay-docker.git
```

您也可以修改源代码以实现自定义功能：

```bash
$ git clone https://github.com/dnomd343/syncplay-docker.git

$ cd ./syncplay-docker/
# some edit...

$ docker build -t syncplay .
```

如果需要构建多架构镜像，请使用 `buildx` 命令：

```bash
$ docker buildx build -t dnomd343/syncplay                    \
    --platform=linux/amd64,linux/386,linux/arm64,linux/arm/v7 \
    https://github.com/dnomd343/syncplay-docker.git --push
```

## 许可证

MIT License ©2026 [@dnomd343](https://github.com/dnomd343)
