## 快速開始

僅需一行命令開啟 [Syncplay](https://syncplay.pl/) 服務，是的，就這麼簡單。

```bash
$ docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.5
```

> 按下 `Ctrl+C` 可終止服務。

<details>

<summary><b>無法訪問 Docker Hub？</b></summary>

<br/>

如果無法訪問 Internet，需要先獲取 OCI 鏡像並複製到儲存媒介。詳情請參見 [offline usage](#Registry) 。

如果您位於中國大陸且無法正常訪問 Docker Hub，可將 `dnomd343/syncplay` 替換為 `ccr.ccs.tencentyun.com/dnomd343/syncplay`，這將使用廣州的 TCR 服務。

---

</details>

如果沒有意外，可在客戶端填寫伺服器 IP 或域名進行驗證，預設端口為 `tcp/8999` 。如果您無法連接，請檢查防火牆設置。

若要在後台運行服務，請使用下面的命令啟動 Syncplay ：

```bash
$ docker run -d --net=host \
    --restart=always --name=syncplay dnomd343/syncplay
```

> 使用 `docker ps -a` 可查看正在運行的容器，使用 `docker rm -f syncplay` 可停止服務。

您可以通過附加參數定制服務，例如要求連接時輸入密碼、禁用聊天，並在進入房間時顯示歡迎語。示例如下：

> 注意：按回車前請先執行 `docker rm -f syncplay` 移除已存在服務，否則會發生衝突。

```bash
$ docker run -d --net=host \
    --restart=always --name=syncplay dnomd343/syncplay \
    --disable-chat --motd='Hello' --password='PASSWD'
```

有時需要重啟伺服器，此時有必要將 Syncplay 持久化保存，也就是把房間數據寫入磁碟。您可以指定一個工作目錄，比如 `/etc/syncplay/`，執行下面命令後，數據會保存到該目錄下的 `rooms.db` 文件。

```bash
$ docker run -d --net=host         \
    --volume /etc/syncplay/:/data/ \
    --restart=always --name=syncplay dnomd343/syncplay \
    --persistent --motd='Persistent Server'
```

該目錄還可用於其他用途。例如添加 `--enable-stats` 選項將啟用統計功能，數據會保存到目錄下的 `stats.db` 文件。您還可以在該目錄中創建 `config.yml` 文件，將配置選項寫入其中。Syncplay 啟動時會自動讀取此文件，無需在命令行中輸入大量參數。

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

部署時啟用 TLS 通常是個好主意（本步驟可選），幸運的是 Syncplay 可以很簡單地做到這點。在開始前，您需要準備域名並將其 DNS 指向當前伺服器，同時準備域名的私鑰和證書文件。

證書可通過 [`acme.sh`](https://acme.sh/) 、[`certbot`](https://certbot.eff.org/) 或其他方式獲取。最終您會得到私鑰和證書文件，Syncplay 需要以下三個文件：

> 某些 CA 可能不會提供 chain 文件，需要您手動獲取，例如 [`whatsmychaincert`](https://whatsmychaincert.com/) 。

+ `cert.pem`：CA 簽發的證書
+ `chain.pem`：CA 證書鏈
+ `privkey.pem`：證書私鑰

例如使用 `acme.sh` 執行下面命令，將域名 `343.re` 的證書保存到 `/etc/ssl/certs/343.re/` 目錄：

```bash
$ acme.sh --install-cert -d 343.re               \
    --cert-file  /etc/ssl/certs/343.re/cert.pem  \
    --ca-file    /etc/ssl/certs/343.re/chain.pem \
    --key-file   /etc/ssl/certs/343.re/privkey.pem
```

準備就緒後，執行以下命令即可啟動一個更安全、更私密的 Syncplay 服務：

```bash
$ docker run -d --net=host                  \
    --volume /etc/syncplay/:/data/          \
    --volume /etc/ssl/certs/343.re/:/certs/ \
    --restart=always --name=syncplay dnomd343/syncplay \
    --enable-tls --motd='Secure Server'
```

> 注意客戶端輸入的伺服器地址必須與證書匹配，否則連接會失敗。

與一些服務不同，Syncplay 的證書更新後無需手動重啟，它會自動檢測證書變化並使用最新版本。此外，Syncplay 服務端的 TLS 具有自適應能力，即使舊版本客戶端不支持 TLS 仍可正常通信，但此時安全加密將無法生效。

## 命令行參數

通過指定以下命令行參數來定制 Syncplay 伺服器：

> 以下參數已針對 Docker 優化，與[官方文檔](https://man.archlinux.org/man/extra/syncplay/syncplay-server.1)存在一定差異，使用時請以本說明為準。

+ `--config [FILE]` ：指定配置文件，預設是 `config.yml` 。

+ `--port [PORT]` ：Syncplay 服務監聽端口，預設是 `8999` 。

+ `--password [PASSWD]` ：連接伺服器的身份驗證密碼，預設不啟用。

+ `--motd [MESSAGE]` ：使用者進入房間時顯示的歡迎文本，預設不啟用。

+ `--salt [TEXT]` ：用於加固密碼的隨機字符串鹽值，預設是空字符串。

+ `--random-salt` ：使用隨機生成的鹽值，僅在未指定 `--salt` 時生效，預設不啟用。

+ `--isolate-rooms` ：啟用房間隔離，用戶無法看到其他房間的信息，預設不啟用。

+ `--disable-chat` ：禁用聊天功能，預設不啟用。

+ `--disable-ready` ：禁用就緒指示器功能，預設不啟用。

+ `--enable-stats` ：啟用伺服器統計功能，數據將保存到 `stats.db` ，預設不啟用。

+ `--enable-tls` ：啟用 TLS 支持，需將證書文件掛載到 `/certs/` 目錄，包括 `cert.pem` 、`chain.pem` 和 `privkey.pem` ，預設不啟用。

+ `--persistent` ：啟用房間數據持久化，信息將保存到 `rooms.db` ，僅在未指定 `--isolate-rooms` 時有效，預設不啟用。

+ `--max-username [NUM]` ：用戶名最大長度，預設是 `16` 。

+ `--max-chat-message [NUM]` ：聊天消息最大長度，預設是 `150` 。

+ `--permanent-rooms [ROOM ...]` ：指定即使播放列表為空也仍會列出的房間，僅在指定 `--persistent` 時有效，預設為空。

+ `--listen-ipv4 [ADDR]` ：在 IPv4 網路上監聽的地址，預設不啟用。

+ `--listen-ipv6 [ADDR]` ：在 IPv6 網路上監聽的地址，預設不啟用。

+ `--version` ：顯示 Syncplay 和 Python 版本，以及 CPU 架構。

> 僅指定 `--listen-ipv4` 時，Syncplay 不會在 IPv6 上監聽；僅指定 `--listen-ipv6` 時，Syncplay 不會在 IPv4 上監聽。若兩者均指定，則啟用雙棧網絡。

使用 `--version` 選項顯示 Syncplay 和 Python 的版本，同時輸出 CPU 架構：

```bash
$ docker run --rm dnomd343/syncplay --version
Syncplay Docker Bootstrap v1.7.5 (Yoitsu 117) [CPython 3.12.13 aarch64]
```

您可以運行下面命令查看幫助信息：

<details>

<summary><b>命令行幫助信息</b></summary>

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

如果需要配置大量選項，每次啟動時輸入大量命令行參數會很麻煩且容易出錯。此時可以將它們寫入配置文件。

在工作目錄中創建 `config.yml` 文件，使用 YAML 格式指定命令行支持的所有參數。Syncplay 啟動時會自動讀取該文件。但是請注意，如果同一參數同時出現在命令行和配置文件中，命令行參數會覆蓋配置文件中的值。

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

您還可以使用 JSON 或 TOML 格式的配置文件，Syncplay 會根據文件後綴自動識別。預設配置文件名為 `config.yml` ，也可以通過 `--config` 參數或 `CONFIG` 環境變數指定其他文件。

## 環境變量

Syncplay 容器還支持通過環境變量配置。僅支持數字、字符串和布爾類型三種字段。環境變量名應全部使用大寫，並把 `-` 替換為 `_`，布爾值使用 `ON` 或 `TRUE` 表示，下面是一個範例：

```bash
$ docker run -d --net=host \
    --env PORT=7999        \
    --env MOTD=Hello       \
    --env DISABLE_CHAT=ON  \
    --restart=always --name=syncplay dnomd343/syncplay
```

如您所見，Syncplay 支持三種配置方式：命令行參數、配置文件和環境變量。優先級從高到低，也就是命令行參數將覆蓋配置文件選項，配置文件將覆蓋環境變量，您可根據需要組合使用。

## Docker Compose

使用 `docker compose` 部署 Syncplay 更加優雅。您需要創建一個 `docker-compose.yml` 文件，內容示例如下：

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

將該文件保存在 `/etc/syncplay/` 也就是工作目錄下，由於 `volumes` 中使用了相對路徑，它也位於工作目錄中。進入該目錄後執行以下命令即可啟動 Syncplay 服務：

```bash
$ docker compose up -d
[+] Running 1/1
✔ Container syncplay Started
```

> 添加 `-d` 參數可讓服務在後台運行。

同樣，您可以映射證書目錄以啟用 TLS，並編輯 `config.yml` 配置更多選項。

## 安全

上述命令中我們使用 `--net=host` 直接將容器接入主機網絡，會暴露外部服務。出於安全考慮，建議使用 `bridge` 網絡並映射 `tcp/8999` 端口，儘管性能可能會略微下降。

```bash
$ docker run -d -p 8999:8999 \
    --restart=always --name=syncplay dnomd343/syncplay
```

預設情況下，Docker 以 root 使用者運行容器，這存在安全風險。本項目構建的鏡像符合 OCI 標準，因此您可以使用 [Podman](https://podman.io/) 完全替代 Docker，Podman 預設以非 root 模式運行。

```bash
$ podman run -d -p 8999:8999 \
    --restart=always --name=syncplay dnomd343/syncplay
```

或者，您也可以使用 Docker [rootless mode](https://docs.docker.com/engine/security/rootless/)，不過配置較為繁瑣。如果只希望繼續使用 Docker，可在構建鏡像時指定 `UID` 和 `GID` ，使容器不再以 root 權限運行。

```bash
# 檢查當前非 root 的 UID 和 GID。
$ id
uid=1000(dnomd343) gid=1000(dnomd343) ...

# 使用獲得的 UID 和 GID 作為構建參數。
$ docker build -t my-syncplay \
    --build-arg USER_UID=1000 \
    --build-arg USER_GID=1000 \
    https://github.com/dnomd343/syncplay-docker.git

$ docker run -d -p 8999:8999 \
    --restart=always --name=syncplay my-syncplay
```

## Registry

本項目發布的鏡像遵循 [OCI 鏡像格式規範](https://github.com/opencontainers/image-spec)，可分發到任何支持 [OCI Distribution 規範](https://github.com/opencontainers/distribution-spec) 的鏡像倉庫。當前工作流中，GitHub Actions 會自動將鏡像分發到以下倉庫：

- Docker Hub: `dnomd343/syncplay`
- Github Package: `ghcr.io/dnomd343/syncplay`
- Tencent Cloud: `ccr.ccs.tencentyun.com/dnomd343/syncplay`

當前支持四種 CPU 架構：`amd64`、`arm64`、`i386` 和 `arm/v7` 。在拉取鏡像時，容器工具會根據主機架構自動選擇合適版本。

您可以將原始 OCI 鏡像拉取後導出為 tar 文件以便離線使用。推薦使用 [skopeo](https://github.com/containers/skopeo.git) 工具達成。

> 您也可使用 `docker save` 導出鏡像，但僅支持單一架構。

```bash
# 归档 1.7.5 版本所有架构的镜像。
$ skopeo copy --all                             \
    docker://docker.io/dnomd343/syncplay:v1.7.5 \
    oci-archive:syncplay-v1.7.5.tar

# 归档 1.7.5 版本 arm64 架构的镜像。
$ skopeo copy --override-os=linux --override-arch=arm64 \
    docker://docker.io/dnomd343/syncplay:v1.7.5         \
    oci-archive:syncplay-v1.7.5-arm64.tar

# 将镜像移到另一台計算機並在 docker 中解壓。
$ docker load < syncplay-v1.7.5.tar
```

## 故障排查

如果遇到錯誤，請先使用 `docker logs syncplay` 查看進程輸出，它通常會提供有用的信息。您也可以通過設置環境變量 `DEBUG=ON` 輸出更詳細日誌。

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

## 高級

由於某些原因，您可能需要更改配置文件路徑或工作目錄，Syncplay 容器支持通過環境變量指定。

+ `TEMP_DIR` ：臨時目錄，不需持久化，默認為 `/tmp/` 。
+ `WORK_DIR` ：工作目錄，用於存儲 Syncplay 相關數據，默認為 `/data/` 。
+ `CERT_DIR` ：證書目錄，用於存放 TLS 證書和私鑰文件，默認為 `/certs/` 。

## 構建鏡像

> 本項目在構建過程中使用了若干 [BuildKit](https://github.com/moby/buildkit.git) 特性（隨 Docker 23.0 及更高版本捆綁）。因此其他構建工具可能會出現相容性問題。

您可以直接從源碼構建鏡像：

```bash
$ docker build -t syncplay https://github.com/dnomd343/syncplay-docker.git
```

您也可以修改源代碼以實現自定義功能：

```bash
$ git clone https://github.com/dnomd343/syncplay-docker.git

$ cd ./syncplay-docker/
# some edit...

$ docker build -t syncplay .
```

如果需要構建多架構鏡像，請使用 `buildx` 命令：

```bash
$ docker buildx build -t dnomd343/syncplay                    \
    --platform=linux/amd64,linux/386,linux/arm64,linux/arm/v7 \
    https://github.com/dnomd343/syncplay-docker.git --push
```

## 许可证

MIT License ©2026 [@dnomd343](https://github.com/dnomd343)
