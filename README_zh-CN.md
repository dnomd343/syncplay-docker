## 快速开始

使用一句命令开启 Syncplay 服务，是的，就这么简单。

```bash
> docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.0
```

> 按下 `Ctrl+C` 将退出服务

如果没有意外，您可以在客户端填入服务器 IP 或域名进行验证，默认端口是 `tcp/8999`。若无法连上，请检查您的防火墙设置。

为了更好地运行服务，我们应当使用以下命令让 Syncplay 在后台运行，并保持启动。

```bash
docker run -d --net=host --restart=always --name=syncplay dnomd343/syncplay
```

> 您可以使用 `docker ps -a` 看到正在运行的服务，还可以使用 `docker rm -f syncplay` 停止服务。

您可以加入更多的参数来实现定制化，例如我们让服务器连接时需要输入密码、禁止聊天、并在进入房间后显示一句欢迎语，使用以下命令。

> 注意在按下回车前，您必须执行 `docker rm -f syncplay` 移除掉原有的服务，否则它们会发生冲突。

```bash
docker run -d --net=host           \
  --restart=always --name=syncplay \
  dnomd343/syncplay --disable-chat \
  --password=PASSWD --motd='HELLO WORLD'
```

服务器在必要的时候会被重启，也可能是 Docker 服务或 Syncplay 需要更新，无论是不是预期中的，这个时候将 Syncplay 持久化是很有必要的，这意味着房间数据将会被保存到磁盘上。您需要选择一个工作目录来保存他们，例如 `/etc/syncplay/`，执行以下命令，数据会被保存到 `rooms.db` 文件中。

```bash
docker run -d --net=host           \
  --restart=always --name=syncplay \
  --volume /etc/syncplay/:/data/   \
  dnomd343/syncplay --persistent
```

这个目录还有更多的用途，例如添加 `--enable-stats` 选项将开启统计功能，数据将被保存到目录下 `stats.db` 这个文件中。您还可以在目录下创建 `config.yml` 文件，将配置参数写在里面，Syncplay 启动时将会自动读取，避免在命令行中键入大量参数。

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

在实际部署时，开启 TLS 总会是一个好主意（当然它不是必要的，这一步可以跳过），幸运的是，Syncplay 可以很简单地做到这一点。在开始前，您需要准备一个域名，并把它的 DNS 解析到当前服务器上，同时，我们必须拥有它的证书文件。

证书的申请可以通过 [`acme.sh`](https://acme.sh/) 、[`certbot`](https://certbot.eff.org/) 或者其他合理的方式进行。总之，您最终会得到一把私钥和一张证书，Syncplay 需要您提供以下三个文件。

+ `cert.pem` ：CA 机构签发的证书
+ `chain.pem` ：CA 机构的证书链
+ `privkey.pem` ：证书的私钥文件

例如在 `acme.sh` 中，可以这样子执行命令，将 `343.re` 这个域名的证书配置保存到 `/etc/ssl/certs/343.re/` 目录下。

```bash
acme.sh --install-cert -d 343.re               \
  --cert-file  /etc/ssl/certs/343.re/cert.pem  \
  --ca-file    /etc/ssl/certs/343.re/chain.pem \
  --key-file   /etc/ssl/certs/343.re/privkey.pem
```

现在我们已经准备好了，只需要执行下面的命令，一个更安全更隐私的 Syncplay 服务将会启动。

```bash
docker run -d --net=host                  \
  --restart=always --name=syncplay        \
  --volume /etc/syncplay/:/data/          \
  --volume /etc/ssl/certs/343.re/:/certs/ \
  dnomd343/syncplay --persistent --enable-tls
```

> 注意客户端的服务器地址必须与证书匹配，否则连接将会失败。

需要说明的是，与有些服务不同，Syncplay 在证书发生更新时不需要手动重启，它会自动检测证书的变化，并使用最新的版本。此外，Syncplay 服务端的 TLS 是自适应的，这意味着，即使是不支持 TLS 的旧版本客户端，它们仍然可以正常通讯，但是注意此时安全加密将不再生效。

## 命令行参数

您可以通过指定以下命令行参数来定制 Syncplay 服务器。

> 以下参数是针对 docker 调整过的，与[官方文档](https://man.archlinux.org/man/extra/syncplay/syncplay-server.1)不完全相同，使用时请以此为准。

+ `--port [PORT]` ：Syncplay 服务器监听端口, 默认为 `8999`

+ `--password [PASSWD]` ：用户登录服务器的密码，默认不启用

+ `--motd [MESSAGE]` ：用户进入房间的欢迎内容，默认不启用

+ `--salt [SALT]` ：密码加盐，指定随机字符串，用于抵抗哈希攻击（例如彩虹表），默认为空字符串

+ `--random-salt` ：使用随机生成的盐，仅当 `--salt` 未指定时生效，默认不启用

+ `--isolate-rooms` ：开启独立房间，用户将看不到其他房间的用户信息，默认不启用

+ `--disable-chat` ：禁止聊天功能，默认不启用

+ `--disable-ready` ：禁止就绪指示器功能，默认不启用

+ `--enable-stats` ：开启服务器统计功能，数据将被保存到 `stats.db` 文件中，默认不启用

+ `--enable-tls` ：开启 TLS 支持, 证书文件需要挂载到 `/certs/` 目录下，包括 `cert.pem` 、`chain.pem` 、`privkey.pem` 三个文件，默认不启用

+ `--persistent` ：开启房间数据持久化，信息将被保存到 `rooms.db` 文件中，仅当 `--isolate-rooms` 未指定时有效，默认不启用

+ `--max-username [N]` ：用户名最大长度，默认为 `150`

+ `--max-chat-message [N]` ：聊天消息最大长度，默认为 `150`

+ `--permanent-rooms [ROOM ...]` ：即使播放列表为空时仍会列出的房间，仅当 `--persistent` 指定时有效，默认为空

您也可以使用以下命令输出帮助信息。

```bash
> docker run --rm syncplay --help
usage: syncplay [-h] [-p PORT] [--password PASSWORD] [--motd MOTD]
                [--salt SALT] [--random-salt] [--isolate-rooms]
                [--disable-chat] [--disable-ready] [--enable-stats]
                [--enable-tls] [--persistent] [--max-username MAX_USERNAME]
                [--max-chat-message MAX_CHAT_MESSAGE]
                [--permanent-rooms [PERMANENT_ROOMS ...]]

Syncplay Docker Bootstrap

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  listen port of syncplay server
  --password PASSWORD   authentication of syncplay server
  --motd MOTD           welcome text after the user enters the room
  --salt SALT           string used to secure passwords
  --random-salt         use a randomly generated salt value
  --isolate-rooms       room isolation enabled
  --disable-chat        disables the chat feature
  --disable-ready       disables the readiness indicator feature
  --enable-stats        enable syncplay server statistics
  --enable-tls          enable tls support of syncplay server
  --persistent          enables room persistence
  --max-username MAX_USERNAME
                        maximum length of usernames
  --max-chat-message MAX_CHAT_MESSAGE
                        maximum length of chat messages
  --permanent-rooms [PERMANENT_ROOMS ...]
                        permanent rooms of syncplay server
```

## 配置文件

如果您配置了较多的选项，每次启动时输入大量命令行参数会是相当麻烦且易出错的事情，这个时候可以将它们写到配置文件中。在工作目录中创建 `config.yml` 文件，它使用 YAML 格式，支持命令行中的所有参数，Syncplay 在启动时会自动读取并加载，但需要注意的是，如果命令行指定了同样的参数，将会覆盖配置文件的选项。

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
permanent-rooms:
  - ROOM_1
  - ROOM_2
  - ROOM_3
motd: |
  Hello, here is a syncplay server.
  More information...
```

## Docker Compose

使用 `docker-compose` 来部署 Syncplay 是一种更优雅的方式，你需要创建一个 `docker-compose.yml` 配置文件，写入以下的示例。

```yaml
# /etc/syncplay/docker-compose.yml
version: '3'
services:
  syncplay:
    container_name: syncplay
    image: dnomd343/syncplay
    network_mode: host
    restart: always
    volumes:
      - ./:/data/
```

我们将这个文件保存在 `/etc/syncplay/` 目录下，由于使用了相对路径，因此它也同样处于工作目录中，在该目录下执行命令启动 Syncplay 服务。

```bash
> docker-compose up
Recreating syncplay ... done
Attaching to syncplay
syncplay    | Welcome to Syncplay server, ver. 1.7.0
```

> 添加 `-d` 选项可以让服务在后台运行。

类似的，您可以映射证书目录来开启 TLS 功能，以及编辑 `config.yml` 文件来配置更多选项。

## 错误排查

如果您遇到了任何错误，请先使用 `docker logs syncplay` 命令打印进程输出内容，它可能包含有用的错误信息，您还可以通过指定环境变量 `DEBUG=ON` 来输出更详细的日志。

```bash
> docker run --rm --env DEBUG=ON dnomd343/syncplay
Command line arguments -> Namespace(port=None, password=None, motd=None, salt=None, random_salt=False, isolate_rooms=False, disable_chat=False, disable_ready=False, enable_stats=False, enable_tls=False, persistent=False, max_username=None, max_chat_message=None, permanent_rooms=None)
Parsed arguments -> {}
Syncplay startup arguments -> ['--port', '8999', '--salt', '']
Welcome to Syncplay server, ver. 1.7.0
```

## 容器构建

您可以直接从源码中构架出镜像，使用以下命令。

```bash
docker build -t syncplay https://github.com/dnomd343/syncplay-docker.git
```

您也可以更改源代码来实现自己的定制。

```bash
> git clone https://github.com/dnomd343/syncplay-docker.git
> cd syncplay-docker/
# some edit...
> docker build -t syncplay .
```

如果您需要多种架构的镜像，请使用 `buildx` 命令构建。

```bash
docker buildx build -t dnomd343/syncplay                    \
  --platform=linux/amd64,linux/386,linux/arm64,linux/arm/v7 \
  https://github.com/dnomd343/syncplay-docker.git --push
```

## 许可证

MIT ©2022 [@dnomd343](https://github.com/dnomd343)
