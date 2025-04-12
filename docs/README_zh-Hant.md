## 快速開始

使用壹句命令開啓 [Syncplay](https://syncplay.pl/) 服務，是的，就這麽簡單。

```bash
> docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.1
```

> 按下 `Ctrl+C` 將退出服務。

如果沒有意外，您可以在客戶端填入服務器 IP 或域名進行驗證，默認端口是 `tcp/8999` 。若無法連上，請檢查您的防火牆設置。

爲了更好地運行服務，我們應當使用以下命令讓 Syncplay 在後台運行，並保持啓動。

```bash
docker run -d --net=host --restart=always --name=syncplay dnomd343/syncplay
```

> 您可以使用 `docker ps -a` 看到正在運行的服務，還可以使用 `docker rm -f syncplay` 停止服務。

您可以加入更多的參數來實現定制化，例如我們讓服務器連接時需要輸入密碼、禁止聊天、並在進入房間後顯示壹句歡迎語，使用以下命令。

> 注意在按下回車前，您必須執行 `docker rm -f syncplay` 移除掉原有的服務，否則它們會發生沖突。

```bash
docker run -d --net=host --restart=always --name=syncplay dnomd343/syncplay \
  --disable-chat --password=PASSWD --motd='HELLO WORLD'
```

服務器在必要的時候會被重啓，也可能是 Docker 服務需要更新，無論是不是預期中的，這個時候將 Syncplay 持久化是很有必要的，這意味著房間數據將會被保存到磁盤上。您需要選擇壹個工作目錄來保存他們，例如 `/etc/syncplay/` ，執行以下命令，數據會被保存到 `rooms.db` 文件中。

```bash
docker run -d --net=host           \
  --restart=always --name=syncplay \
  --volume /etc/syncplay/:/data/   \
  dnomd343/syncplay --persistent
```

這個目錄還有更多的用途，例如添加 `--enable-stats` 選項將開啓統計功能，數據將被保存到目錄下 `stats.db` 這個文件中。您還可以在目錄下創建 `config.yml` 文件，將配置參數寫在裏面，Syncplay 啓動時將會自動讀取，避免在命令行中鍵入大量參數。

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

在實際部署時，開啓 TLS 總會是壹個好主意（當然它不是必要的，這壹步可以跳過），幸運的是，Syncplay 可以很簡單地做到這壹點。在開始前，您需要准備壹個域名，並把它的 DNS 解析到當前服務器上，同時，我們必須擁有它的證書文件。

證書的申請可以通過 [`acme.sh`](https://acme.sh/) 、[`certbot`](https://certbot.eff.org/) 或者其他合理的方式進行。總之，您最終會得到壹把私鑰和壹張證書，Syncplay 需要您提供以下三個文件。

+ `cert.pem` ：CA 機構簽發的證書
+ `chain.pem` ：CA 機構的證書鏈
+ `privkey.pem` ：證書的私鑰文件

例如在 `acme.sh` 中，可以這樣子執行命令，將 `343.re` 這個域名的證書配置保存到 `/etc/ssl/certs/343.re/` 目錄下。

```bash
acme.sh --install-cert -d 343.re               \
  --cert-file  /etc/ssl/certs/343.re/cert.pem  \
  --ca-file    /etc/ssl/certs/343.re/chain.pem \
  --key-file   /etc/ssl/certs/343.re/privkey.pem
```

現在我們已經准備好了，只需要執行下面的命令，壹個更安全更隱私的 Syncplay 服務將會啓動。

```bash
docker run -d --net=host                  \
  --restart=always --name=syncplay        \
  --volume /etc/syncplay/:/data/          \
  --volume /etc/ssl/certs/343.re/:/certs/ \
  dnomd343/syncplay --persistent --enable-tls
```

> 注意客戶端的服務器地址必須與證書匹配，否則連接將會失敗。

需要說明的是，與有些服務不同，Syncplay 在證書發生更新時不需要手動重啓，它會自動檢測證書的變化，並使用最新的版本。此外，Syncplay 服務端的 TLS 是自適應的，這意味著，即使是不支持 TLS 的舊版本客戶端，它們仍然可以正常通訊，但是注意此時安全加密將不再生效。

## 命令行參數

您可以通過指定以下命令行參數來定制 Syncplay 服務器。

> 以下參數是針對 docker 調整過的，與[官方文檔](https://man.archlinux.org/man/extra/syncplay/syncplay-server.1)不完全相同，使用時請以此爲准。

+ `--port [PORT]` ：Syncplay 服務器監聽端口, 默認爲 `8999`

+ `--password [PASSWD]` ：用戶登錄服務器的密碼，默認不啓用

+ `--motd [MESSAGE]` ：用戶進入房間的歡迎內容，默認不啓用

+ `--salt [TEXT]` ：密碼加鹽，指定隨機字符串，用于抵抗哈希攻擊（例如彩虹表），默認爲空字符串

+ `--random-salt` ：使用隨機生成的鹽，僅當 `--salt` 未指定時生效，默認不啓用

+ `--isolate-rooms` ：開啓獨立房間，用戶將看不到其他房間的用戶信息，默認不啓用

+ `--disable-chat` ：禁止聊天功能，默認不啓用

+ `--disable-ready` ：禁止就緒指示器功能，默認不啓用

+ `--enable-stats` ：開啓服務器統計功能，數據將被保存到 `stats.db` 文件中，默認不啓用

+ `--enable-tls` ：開啓 TLS 支持, 證書文件需要挂載到 `/certs/` 目錄下，包括 `cert.pem` 、`chain.pem` 、`privkey.pem` 三個文件，默認不啓用

+ `--persistent` ：開啓房間數據持久化，信息將被保存到 `rooms.db` 文件中，僅當 `--isolate-rooms` 未指定時有效，默認不啓用

+ `--max-username [NUM]` ：用戶名最大長度，默認爲 `150`

+ `--max-chat-message [NUM]` ：聊天消息最大長度，默認爲 `150`

+ `--permanent-rooms [ROOM ...]` ：即使播放列表爲空時仍會列出的房間，僅當 `--persistent` 指定時有效，默認爲空

+ `--listen-ipv4 [ADDR]` ：自定義 Syncplay 服務在 IPv4 網絡上的監聽地址，默認不啓用

+ `--listen-ipv6 [ADDR]` ：自定義 Syncplay 服務在 IPv6 網絡上的監聽地址，默認不啓用

> 當您僅指定 `--listen-ipv4` 時，Syncplay 將不會在 IPv6 上監聽，反之同理。當兩者均指定時，Syncplay 將工作在雙棧網絡下。

您也可以使用以下命令輸出幫助信息。

```bash
> docker run --rm syncplay --help
usage: syncplay [-h] [-p PORT] [--password PASSWD] [--motd MESSAGE]
                [--salt TEXT] [--random-salt] [--isolate-rooms]
                [--disable-chat] [--disable-ready] [--enable-stats]
                [--enable-tls] [--persistent] [--max-username NUM]
                [--max-chat-message NUM] [--permanent-rooms [ROOM ...]]
                [--listen-ipv4 INTERFACE] [--listen-ipv6 INTERFACE]

Syncplay Docker Bootstrap

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  listen port of syncplay server
  --password PASSWD     authentication of syncplay server
  --motd MESSAGE        welcome text after the user enters the room
  --salt TEXT           string used to secure passwords
  --random-salt         use a randomly generated salt value
  --isolate-rooms       room isolation enabled
  --disable-chat        disables the chat feature
  --disable-ready       disables the readiness indicator feature
  --enable-stats        enable syncplay server statistics
  --enable-tls          enable tls support of syncplay server
  --persistent          enables room persistence
  --max-username NUM    maximum length of usernames
  --max-chat-message NUM
                        maximum length of chat messages
  --permanent-rooms [ROOM ...]
                        permanent rooms of syncplay server
  --listen-ipv4 INTERFACE
                        listening address of ipv4
  --listen-ipv6 INTERFACE
                        listening address of ipv6
```

## 配置文件

如果您配置了較多的選項，每次啓動時輸入大量命令行參數會是相當麻煩且易出錯的事情，這個時候可以將它們寫到配置文件中。在工作目錄中創建 `config.yml` 文件，它使用 YAML 格式，支持命令行中的所有參數，Syncplay 在啓動時會自動讀取並加載，但需要注意的是，如果命令行指定了同樣的參數，將會覆蓋配置文件的選項。

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

## 環境變量

Syncplay 容器還支持通過環境變量來配置，它支持數字、字符串以及布爾三種類型的字段，這裏意味著 `permanent-rooms` 不被支持。環境變量全部使用大寫命名，並將 `-` 替換爲 `_` ，布爾值使用 `ON` 或者 `TRUE` 表示，下面是壹個使用環境變量的例子。

```bash
docker run -d --net=host --restart=always --name=syncplay \
  --env PORT=7999 --env MOTD=Hello --env DISABLE_READY=ON \
  dnomd343/syncplay
```

您或許已經注意到了，我們支持三種配置方式：命令行參數、配置文件和環境變量，它們的優先級由高到低，也就是命令行參數將覆蓋配置文件的選項，配置文件將覆蓋環境變量的值，您可以搭配使用它們。

## Docker Compose

使用 `docker-compose` 來部署 Syncplay 是壹種更優雅的方式，妳需要創建壹個 `docker-compose.yml` 配置文件，寫入以下的示例。

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

我們將這個文件保存在 `/etc/syncplay/` 目錄下，由于使用了相對路徑，因此它也同樣處于工作目錄中，在該目錄下執行命令啓動 Syncplay 服務。

```bash
> docker-compose up
Recreating syncplay ... done
Attaching to syncplay
syncplay    | Welcome to Syncplay server, ver. 1.7.1
```

> 添加 `-d` 選項可以讓服務在後台運行。

類似的，您可以映射證書目錄來開啓 TLS 功能，以及編輯 `config.yml` 文件來配置更多選項。

## 錯誤排查

如果您遇到了任何錯誤，請先使用 `docker logs syncplay` 命令打印進程輸出內容，它可能包含有用的錯誤信息，您還可以通過指定環境變量 `DEBUG=ON` 來輸出更詳細的日志。

```bash
> docker run --rm --env DEBUG=ON dnomd343/syncplay
Bootstrap options -> [('port', <class 'int'>, False), ('password', <class 'str'>, False), ('motd', <class 'str'>, False), ('salt', <class 'str'>, False), ('random_salt', <class 'bool'>, False), ('isolate_rooms', <class 'bool'>, False), ('disable_chat', <class 'bool'>, False), ('disable_ready', <class 'bool'>, False), ('enable_stats', <class 'bool'>, False), ('enable_tls', <class 'bool'>, False), ('persistent', <class 'bool'>, False), ('max_username', <class 'int'>, False), ('max_chat_message', <class 'int'>, False), ('permanent_rooms', <class 'str'>, True), ('listen_ipv4', <class 'str'>, False), ('listen_ipv6', <class 'str'>, False)]
Environment variables -> environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': '0a28a2e2ea50', 'DEBUG': 'ON', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.10.13', 'PYTHON_PIP_VERSION': '23.0.1', 'PYTHON_SETUPTOOLS_VERSION': '65.5.1', 'PYTHON_GET_PIP_URL': 'https://github.com/pypa/get-pip/raw/4cfa4081d27285bda1220a62a5ebf5b4bd749cdb/public/get-pip.py', 'PYTHON_GET_PIP_SHA256': '9cc01665956d22b3bf057ae8287b035827bfd895da235bcea200ab3b811790b6', 'PYTHONUNBUFFERED': '1', 'HOME': '/root'})
Environment options -> {}
Configure file -> {}
Configure file options -> {}
Command line arguments -> Namespace(port=None, password=None, motd=None, salt=None, random_salt=False, isolate_rooms=False, disable_chat=False, disable_ready=False, enable_stats=False, enable_tls=False, persistent=False, max_username=None, max_chat_message=None, permanent_rooms=None, listen_ipv4=None, listen_ipv6=None)
Command line options -> {}
Bootstrap final options -> {}
Syncplay startup arguments -> ['--port', '8999', '--salt', '']
Welcome to Syncplay server, ver. 1.7.1
```

## 高級選項

出于壹些原因，您可能需要更改配置文件或工作目錄的位置，這在 Syncplay 容器中是可行的，它需要您使用環境變量來指定。

+ `TEMP_DIR` ：臨時目錄，它不需要被持久化，默認爲 `/tmp/`

+ `WORK_DIR` ：工作目錄，它存儲和 Syncplay 相關的數據，默認爲 `/data/`

+ `CERT_DIR` ：證書目錄，它用于存放 TLS 相關的證書和私鑰文件，默認爲 `/certs/`

+ `CONFIG` ：配置文件，它定義引導腳本讀取的 YAML 配置，默認爲 `config.yml`

## 容器構建

您可以直接從源碼中構架出鏡像，使用以下命令。

```bash
docker build -t syncplay https://github.com/dnomd343/syncplay-docker.git
```

您也可以更改源代碼來實現自己的定制。

```bash
> git clone https://github.com/dnomd343/syncplay-docker.git
> cd syncplay-docker/
# some edit...
> docker build -t syncplay .
```

如果您需要多種架構的鏡像，請使用 `buildx` 命令構建。

```bash
docker buildx build -t dnomd343/syncplay                    \
  --platform=linux/amd64,linux/386,linux/arm64,linux/arm/v7 \
  https://github.com/dnomd343/syncplay-docker.git --push
```

## 許可證

MIT ©2023 [@dnomd343](https://github.com/dnomd343)
