## クイックスタート

コマンド1つで [Syncplay](https://syncplay.pl/) サービスをオンにできる。

```bash
> docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.1
```

> `Ctrl+C` を押すとサービスを終了します。

何もなければ、サーバーの IP またはドメイン名を記入することで、クライアント側で認証することができ、デフォルトのポートは `tcp/8999` である。接続できない場合は、ファイアウォールの設定を確認してください。

サービスをより良く実行するために、以下のコマンドで Syncplay をバックグラウンドで実行させ、起動させておく必要がある。

```bash
docker run -d --net=host --restart=always --name=syncplay dnomd343/syncplay
```

> `docker ps -a` で実行中のサービスを確認し、`docker rm -f syncplay` で停止させることができる。

サーバー接続時にパスワードを要求する、チャットを禁止する、入室後にウェルカムメッセージを表示するなどのカスタマイズを実現するには、次のコマンドを使用します。

> Enter キーを押す前に、`docker rm -f syncplay` を実行して元のサービスを削除する必要があることに注意してください。そうしないと、サービスが競合します。

```bash
docker run -d --net=host --restart=always --name=syncplay dnomd343/syncplay \
  --disable-chat --password=PASSWD --motd='HELLO WORLD'
```

必要に応じてサーバーが再起動されるか、Docker サービスの更新が必要になる場合があります。期待されるかどうかに関係なく、この時点では Syncplay を永続化する必要があります。これは、ルーム データがディスクに保存されることを意味します。`/etc/syncplay/` などの作業ディレクトリを選択して保存する必要があります。次のコマンドを実行すると、データが `rooms.db` ファイルに保存されます。

```bash
docker run -d --net=host           \
  --restart=always --name=syncplay \
  --volume /etc/syncplay/:/data/   \
  dnomd343/syncplay --persistent
```

このディレクトリにはさらに用途があり、たとえば、`--enable-stats` オプションを追加すると統計機能が有効になり、データがディレクトリ内のファイル `stats.db` に保存されます。ディレクトリに `config.yml` ファイルを作成し、その中に設定パラメータを書き込むこともできます。Syncplay は起動時に自動的にファイルを読み込むため、コマンド ラインに多数のパラメータを入力する必要がなくなります。

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

実際のデプロイに関しては、常に TLS をオンにすることをお勧めする（もちろん必要ではないので、このステップは省略できる）。幸いなことに、Syncplay はこれを非常に簡単に行うことができる。開始する前に、ドメイン名を用意し、その DNS を現在のサーバーに解決する必要がある。 また、その証明書ファイルも用意しなければならない。

証明書の申請は、[`acme.sh`](https://acme.sh/) 、[`certbot`](https://certbot.eff.org/) 、またはその他の合理的な方法で行うことができる。いずれにせよ、秘密鍵と証明書ができあがり、Syncplay は以下の3つのファイルを要求する。

+ `cert.pem` ：CA 組織が発行した証明書
+ `chain.pem` ：CA 認証局の証明書チェーン
+ `privkey.pem` ：証明書の秘密鍵ファイル

たとえば、`acme.sh` では、次のようなコマンドを実行して、ドメイン `343.re` の証明書設定を `/etc/ssl/certs/343.re/` ディレクトリに保存することができる。

```bash
acme.sh --install-cert -d 343.re               \
  --cert-file  /etc/ssl/certs/343.re/cert.pem  \
  --ca-file    /etc/ssl/certs/343.re/chain.pem \
  --key-file   /etc/ssl/certs/343.re/privkey.pem
```

これで準備が整ったので、以下のコマンドを実行するだけで、より安全でプライベートな Syncplay サービスが開始される。

```bash
docker run -d --net=host                  \
  --restart=always --name=syncplay        \
  --volume /etc/syncplay/:/data/          \
  --volume /etc/ssl/certs/343.re/:/certs/ \
  dnomd343/syncplay --persistent --enable-tls
```

> クライアントのサーバー・アドレスが証明書と一致しなければ、接続に失敗することに注意してください。

一部のサービスとは異なり、Syncplay は証明書の更新時に手動で再起動する必要がなく、証明書の変更を自動的に検出し、最新バージョンを使用します。 さらに、Syncplay サーバー上の TLS は適応型です。つまり、TLS をサポートしていない古いバージョンのクライアントでも通常どおり通信できますが、現時点ではセキュリティ暗号化が有効ではなくなることに注意してください。

## コマンドラインパラメータ

以下のコマンドラインパラメーターを指定することで、Syncplay サーバーをカスタマイズできます。

> 以下のパラメータはドッカー用に調整されており、[公文書](https://man.archlinux.org/man/extra/syncplay/syncplay-server.1)とまったく同じではないので、そのまま使ってほしい。

+ `--port [PORT]` ：Syncplay サーバーのリスニング ポート、デフォルトは `8999` です。

+ `--password [PASSWD]` ：ユーザーがサーバーにログインするためのパスワード。デフォルトでは有効になっていません。

+ `--motd [MESSAGE]` ：ルームに入室するユーザーに対するウェルカム コンテンツは、デフォルトでは有効になっていません。

+ `--salt [TEXT]` ：ハッシュ攻撃 (レインボー テーブルなど) に対抗するためにランダムな文字列を指定するパスワード ソルティングは、デフォルトで空の文字列になります。

+ `--random-salt` ：ランダムに生成されたソルトを使用します。`--salt` が指定されていない場合にのみ有効になり、デフォルトでは有効になりません。

+ `--isolate-rooms` ：独立したルームを有効にすると、ユーザーは他のルームのユーザー情報を表示できなくなります (デフォルトでは有効になっていません)。

+ `--disable-chat` ：チャット機能を無効にします。デフォルトでは有効になっていません。

+ `--disable-ready` ：デフォルトでは有効になっていない準備完了インジケーター機能を無効にします。

+ `--enable-stats` ：サーバー統計機能を有効にすると、データは `stats.db` ファイルに保存されますが、デフォルトでは有効になっていません。

+ `--enable-tls` ：TLS サポートを有効にするには、デフォルトでは有効になっていない `cert.pem`、`chain.pem`、および `privkey.pem` を含む証明書ファイルを `/certs/` ディレクトリにマウントする必要があります。

+ `--persistent` ：ルーム データの永続性を有効にすると、情報は `rooms.db` ファイルに保存されます。これは、`--isolate-rooms` が指定されておらず、デフォルトで有効になっていない場合にのみ有効です。

+ `--max-username [NUM]` ：ユーザー名の最大長。デフォルトは `150` です。

+ `--max-chat-message [NUM]` ：チャット メッセージの最大長。デフォルトは `150` です。

+ `--permanent-rooms [ROOM ...]` ：プレイリストが空の場合でもリストに表示されるルームは、`--persistent` が指定されている場合にのみ有効で、デフォルトは空です。

+ `--listen-ipv4 [ADDR]` ：IPv4 ネットワーク上の Syncplay サービスのリスニング アドレスをカスタマイズします。デフォルトでは有効になっていません。

+ `--listen-ipv6 [ADDR]` ：IPv6 ネットワーク上の Syncplay サービスのリスニング アドレスをカスタマイズします。デフォルトでは有効になっていません。

> `--listen-ipv4` のみを指定した場合、Syncplay は IPv6 でリッスンしません。逆も同様です。 両方を指定すると、Syncplay はデュアルスタック ネットワークで動作します。

以下のコマンドでヘルプ情報を出力することもできる。

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

## 設定ファイル

多くのオプションを設定している場合、起動するたびにたくさんのコマンドライン引数を入力するのは面倒だし、エラーになりやすい。作業ディレクトリに `config.yml` ファイルを作成します。このファイルはYAMLフォーマットを使用し、コマンドラインからのすべてのパラメータをサポートします。ただし、同じパラメーターがコマンドラインで指定された場合は、コンフィギュレーション・ファイルのオプションより優先される。

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

## 環境変数

Syncplay コンテナは環境変数による設定もサポートしており、数値、文字列、ブーリアンフィールドをサポートしている。つまり、`permanent-rooms` はサポートされていない。環境変数の名前はすべて大文字で、`-` は `_` に置き換えられ、ブーリアン値は `ON` または `TRUE` で示されます、以下は環境変数の使用例である。

```bash
docker run -d --net=host --restart=always --name=syncplay \
  --env PORT=7999 --env MOTD=Hello --env DISABLE_READY=ON \
  dnomd343/syncplay
```

お気づきかもしれませんが、コマンド ライン パラメータ、設定ファイル、環境変数という 3 つの設定方法がサポートされています。それらの優先順位は高から低の順です。つまり、コマンド ライン パラメータは設定ファイルのオプションをオーバーライドし、設定ファイルは環境変数の値をオーバーライドする場合は、それらを一緒に使用できます。

## Docker Compose

`docker-compose` を使用して Syncplay をデプロイするのはよりエレガントな方法であり、`docker-compose.yml` 設定ファイルを作成し、次の例を記述する必要があります。

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

このファイルを `/etc/syncplay/` ディレクトリに保存します。相対パスを使用するため、作業ディレクトリにもあります。このディレクトリでコマンドを実行して、Syncplay サービスを開始します。

```bash
> docker-compose up
Recreating syncplay ... done
Attaching to syncplay
syncplay    | Welcome to Syncplay server, ver. 1.7.1
```

> `-d` オプションを追加すると、サービスをバックグラウンドで実行できるようになります。

同様に、証明書ディレクトリをマップして TLS 機能を有効にし、`config.yml` ファイルを編集して追加のオプションを構成できます。

## トラブルシューティング

エラーが発生した場合は、まず `docker logs syncplay` コマンドを使用してプロセス出力を印刷してください。これには、有用なエラー情報が含まれている可能性があります。また、環境変数 `DEBUG=ON` を指定することで、より詳細なログを出力することもできます。

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

## 高度なオプション

何らかの理由で、構成ファイルまたは作業ディレクトリの場所を変更する必要がある場合がありますが、これは Syncplay コンテナで可能であり、環境変数を使用して指定する必要があります。

+ `TEMP_DIR` ：一時ディレクトリ。永続化する必要はありません。デフォルトは `/tmp/` です。

+ `WORK_DIR` ：Syncplay に関連するデータを保存する作業ディレクトリは、デフォルトで `/data/` に設定されます。

+ `CERT_DIR` ：証明書ディレクトリ。TLS 関連の証明書と秘密鍵ファイルを保存するために使用されます。デフォルトは `/certs/` です。

+ `CONFIG` ：ブートストラップ スクリプトによって読み取られる YAML 構成を定義する構成ファイルは、デフォルトで「config.yml」になります。

## コンテナのビルド

次のコマンドを使用して、ソース コードから直接イメージをビルドできます。

```bash
docker build -t syncplay https://github.com/dnomd343/syncplay-docker.git
```

ソース コードを変更して独自のカスタマイズを実装することもできます。

```bash
> git clone https://github.com/dnomd343/syncplay-docker.git
> cd syncplay-docker/
# some edit...
> docker build -t syncplay .
```

複数のアーキテクチャのイメージが必要な場合は、`buildx` コマンドを使用してビルドしてください。

```bash
docker buildx build -t dnomd343/syncplay                    \
  --platform=linux/amd64,linux/386,linux/arm64,linux/arm/v7 \
  https://github.com/dnomd343/syncplay-docker.git --push
```

## ライセンス

MIT ©2023 [@dnomd343](https://github.com/dnomd343)
