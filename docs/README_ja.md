## クイックスタート

単一のコマンドを使用して、[Syncplay](https://syncplay.pl/) サービスを開始します。これだけで完了です。

```bash
$ docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.5
```

> `Ctrl+C` を押すと、サービスが終了します。

<details>

<summary><b>Docker Hub にアクセスできませんか?</b></summary>

<br/>

インターネットにアクセスできない場合は、OCI イメージを取得してストレージ媒体にコピーする必要があります。詳細については、[オフライン使用](#Registry)を参照してください。

中国本土にいて通常 Docker Hub にアクセスできない場合は、`dnomd343/syncplay` を `ccr.ccs.tencentyun.com/dnomd343/syncplay` に置き換えることができます。これにより、広州の TCR サービスを使用します。

---

</details>

特に問題がない場合は、クライアントでサーバーの IP アドレスまたはドメイン名を入力して確認できます。デフォルトポートは `tcp/8999` です。接続できない場合はファイアウォールの設定を確認してください。

サービスをバックグラウンドで実行するには、以下のコマンドを使用して Syncplay を開始できます：

```bash
$ docker run -d --net=host \
    --restart=always --name=syncplay dnomd343/syncplay
```

> `docker ps -a` を使用して実行中のコンテナを確認し、`docker rm -f syncplay` でサービスを停止できます。

サービスをカスタマイズするために、追加の引数を指定することも可能です。たとえば、サーバーに接続する際にパスワードが必要になるように設定したり、チャットを無効にしたり、ルームに入る際にウェルカムメッセージを表示することができます。次のコマンドを使用できます：

> Enter を押す前に、必ず `docker rm -f syncplay` を実行して既存のサービスを削除してください。そうしないと、競合が発生します。

```bash
$ docker run -d --net=host \
    --restart=always --name=syncplay dnomd343/syncplay \
    --disable-chat --motd='Hello' --password='PASSWD'
```

サーバーを再起動する必要がある場合があります。この場合、Syncplay を永続化することが必要です。これは、ルームデータをディスクに保存することを意味します。例えば、作業ディレクトリを `/etc/syncplay/` に設定し、次のコマンドを実行します。データは作業ディレクトリの `rooms.db` ファイルに保存されます。

```bash
$ docker run -d --net=host         \
    --volume /etc/syncplay/:/data/ \
    --restart=always --name=syncplay dnomd343/syncplay \
    --persistent --motd='Persistent Server'
```

このディレクトリは追加の目的にも使用できます。たとえば、`--enable-stats` オプションを追加すると、統計が有効になり、データがそのディレクトリ内の `stats.db` ファイルに保存されます。また、ディレクトリ内に `config.yml` ファイルを作成し、そこに構成オプションを書き込むことができます。Syncplay は起動時に自動的にこのファイルを読み込むため、コマンドラインに多数の引数を入力する必要はありません。

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

デプロイ時には、TLS を有効にすることをお勧めします（このステップはオプションであり、省略することもできます）。幸いにも、Syncplay はこれを簡単に実施できます。開始する前に、ドメイン名を準備し、その DNS を現在のサーバーにポイントする必要があります。また、ドメインのプライベートキーと証明書ファイルが必要です。

証明書は [`acme.sh`](https://acme.sh/) や [`certbot`](https://certbot.eff.org/) その他の適切な方法で取得できます。いずれにせよ、プライベートキーと証明書ファイルを取得することになり、Syncplay には以下の3つのファイルを提供する必要があります：

> 一部の CA ではチェインファイルが提供されない場合があります。手動で取得する必要があります。例えば [`whatsmychaincert`](https://whatsmychaincert.com/) のようなサービスを利用してください。

+ `cert.pem` : CA によって発行された証明書。
+ `chain.pem` : CA 証明書チェイン。
+ `privkey.pem` : 証明書のプライベートキー。

例えば、`acme.sh` を使用して、次のコマンドを実行することで、ドメイン名 `343.re` のプライベートキーおよび証明書ファイルを `/etc/ssl/certs/343.re/` ディレクトリに保存できます。

```bash
$ acme.sh --install-cert -d 343.re               \
    --cert-file  /etc/ssl/certs/343.re/cert.pem  \
    --ca-file    /etc/ssl/certs/343.re/chain.pem \
    --key-file   /etc/ssl/certs/343.re/privkey.pem
```

すべての準備が整ったら、次のコマンドを実行するだけで、より安全でプライベートな Syncplay サービスが開始されます。

```bash
$ docker run -d --net=host                  \
    --volume /etc/syncplay/:/data/          \
    --volume /etc/ssl/certs/343.re/:/certs/ \
    --restart=always --name=syncplay dnomd343/syncplay \
    --enable-tls --motd='Secure Server'
```

> クライアントが入力したサーバーアドレスは証明書と一致する必要があります。それ以外の場合、接続は失敗します。

いくつかのサービスとは異なり、Syncplay は証明書が更新されても手動で再起動する必要はありません。証明書の変更を自動的に検出し、最新のバージョンを使用します。また、Syncplay サーバーの TLS は適応性があります。これは、TLS をサポートしない古いバージョンのクライアントでも正常に通信できることを意味しますが、この場合はセキュリティ暗号化が機能しない点に注意してください。

## コマンドライン引数

次のコマンドライン引数を指定することにより、Syncplay サーバーをカスタマイズできます。

> 以下のパラメータは Docker 用に最適化されており、一部公式ドキュメントとの違いがあります。使用する際は、現在のドキュメントを参照してください。

+ `--config [FILE]` : 構成ファイルを指定します。デフォルトは `config.yml` です。

+ `--port [PORT]` : Syncplay サービスのリッスンポートで、デフォルトは `8999` です。

+ `--password [PASSWD]` : サーバーに接続する際の認証で、デフォルトでは無効です。

+ `--motd [MESSAGE]` : ユーザーがルームに入った後のウェルカムメッセージで、デフォルトでは無効です。

+ `--salt [TEXT]` : パスワードを保護するために使用するランダム文字列を指定します。デフォルトは空です。

+ `--random-salt` : ランダム生成された塩値を使用します。`--salt` が指定されていない場合に有効で、デフォルトでは無効です。

+ `--isolate-rooms` : ルームの分離を有効にします。ユーザーは自分のルーム以外の情報を表示できません。デフォルトでは無効です。

+ `--disable-chat` : チャット機能を無効にします。デフォルトでは無効です。

+ `--disable-ready` : 準備インジケーター機能を無効にします。デフォルトでは無効です。

+ `--enable-stats` : サーバー統計機能を有効にします。データは `stats.db` ファイルに保存され、デフォルトでは無効です。

+ `--enable-tls` : TLS サポートを有効にします。証明書ファイルは `/certs/` ディレクトリにマウントする必要があります。デフォルトでは無効です。

+ `--persistent` : ルームデータの永続化を有効にします。情報は `rooms.db` ファイルに保存され、`--isolate-rooms` が指定されていない場合にのみ有効です。

+ `--max-username [NUM]` : ユーザー名の最大長で、デフォルトは `16` です。

+ `--max-chat-message [NUM]` : チャットメッセージの最大長で、デフォルトは `150` です。

+ `--permanent-rooms [ROOM ...]` : プレイリストが空でもリストに残るルームのリストを指定します。`--persistent` が指定されている場合のみ有効で、デフォルトは空です。

+ `--listen-ipv4 [ADDR]` : Syncplay サービスの IPv4 ネットワークのリッスンアドレスで、デフォルトでは無効です。

+ `--listen-ipv6 [ADDR]` : Syncplay サービスの IPv6 ネットワークのリッスンアドレスで、デフォルトでは無効です。

> `--listen-ipv4` のみを指定すると、Syncplay は IPv6 をリッスンしません。逆も同様です。両方のオプションが提供されると、Syncplay はデュアルスタックネットワーキングで動作します。

`--version` オプションを使用して、Syncplay と Python のバージョン、および CPU アーキテクチャを表示できます。

```bash
$ docker run --rm dnomd343/syncplay --version
Syncplay Docker Bootstrap v1.7.5 (Yoitsu 117) [CPython 3.12.13 aarch64]
```

また、次のコマンドを使用してヘルプ情報を出力できます。

<details>

<summary><b>コマンドラインのヘルプメッセージ</b></summary>

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

## 設定ファイル

多くのオプションを設定する必要がある場合、毎回多くのコマンドライン引数を入力するのは手間がかかり、エラーの原因となります。代わりに、それらを設定ファイルに書き込むことができます。

作業ディレクトリに `config.yml` ファイルを作成することで、YAML 形式を使用してコマンドラインでサポートされている任意の引数を指定できます。Syncplay は起動時に自動的にこのファイルを読み込みます。ただし、同じ引数が両方で指定された場合、コマンドライン引数が設定ファイルの内容を上書きします。

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

設定ファイルには JSON または TOML 形式も使用でき、ファイルの拡張子で識別されます。デフォルトの設定ファイル名は `config.yml` ですが、`--config` パラメータや `CONFIG` 環境変数を使用することで異なるファイルを指定することもできます。

## 環境変数

Syncplay コンテナは環境変数を通じての構成もサポートしています。サポートされているのは、数値、文字列、ブーリアンの三種類のフィールドのみです。環境変数名は大文字で、`-` を `_` に置き換え、ブーリアン値は `ON` または `TRUE` で表現します。以下は環境変数を用いて設定する例です。

```bash
$ docker run -d --net=host \
    --env PORT=7999        \
    --env MOTD=Hello       \
    --env DISABLE_CHAT=ON  \
    --restart=always --name=syncplay dnomd343/syncplay
```

ご覧のとおり、Syncplay の設定方法は3つあります: コマンドライン引数、設定ファイル、環境変数です。優先順位は高いものから低いものへ、つまりコマンドライン引数が設定ファイルのオプションを上書きし、設定ファイルが環境変数のオプションを上書きします。必要に応じて組み合わせることができます。

## Docker Compose

`docker compose` を使用して Syncplay をデプロイすることは、よりエレガントな方法です。`docker-compose.yml` 構成ファイルを作成し、以下の例を書きます。

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
      - /etc/ssl/certs/343.re/:/certs/  # TLS を有効にする場合のみ
```

このファイルを `/etc/syncplay/` つまり作業ディレクトリに保存します。`volumes` オプションで相対パスが使用されているため、これも作業ディレクトリに存在します。このディレクトリで次のコマンドを実行して Syncplay サービスを開始します。

```bash
$ docker compose up -d
[+] Running 1/1
✔ Container syncplay Started
```

> `-d` オプションを追加することで、サービスをバックグラウンドで実行できます。

同様に、証明書ディレクトリをマッピングして TLS 機能を有効にし、`config.yml` ファイルを編集して追加のオプションを設定できます。

## セキュリティ

上記のコマンドでは、`--net=host` を使用して外部サービスを公開しています。これにより、コンテナがホストネットワークに直接アクセスできるようになります。しかし、セキュリティの観点からは、`bridge` ネットワークを使用し、`tcp/8999` ポートをマッピングすることをお勧めします。これにより、わずかなパフォーマンス低下が生じる場合があります。

```bash
$ docker run -d -p 8999:8999 \
    --restart=always --name=syncplay dnomd343/syncplay
```

デフォルトでは、Docker はコンテナを root ユーザーとして実行します。これはセキュリティリスクを伴います。このプロジェクトでビルドされたイメージは OCI 標準に準拠しているため、[Podman](https://podman.io/) を完全に置き換えて使用でき、デフォルトでは非 root モードで実行されます。

```bash
$ podman run -d -p 8999:8999 \
    --restart=always --name=syncplay dnomd343/syncplay
```

あるいは、Docker の [rootless mode](https://docs.docker.com/engine/security/rootless/) を使用することもできますが、構成が非常に面倒です。Docker のみを使用したい場合は、イメージをビルドする際に `UID` と `GID` を指定することで、コンテナに root 権限を持たせないようにできます。

```bash
# 現在の非 root UID と GID 値を確認します。
$ id
uid=1000(dnomd343) gid=1000(dnomd343) ...

# 取得した UID と GID 値をビルド引数として使用します。
$ docker build -t my-syncplay \
    --build-arg USER_UID=1000 \
    --build-arg USER_GID=1000 \
    https://github.com/dnomd343/syncplay-docker.git

$ docker run -d -p 8999:8999 \
    --restart=always --name=syncplay my-syncplay
```

## レジストリ

このプロジェクトからリリースされるイメージは、[OCI イメージフォーマット仕様](https://github.com/opencontainers/image-spec) に準拠しており、[OCI ディストリビューション仕様](https://github.com/opencontainers/distribution-spec) をサポートする任意のレジストリで配布可能です。現在のワークフローでは、GitHub Actions が自動的にイメージを以下のレジストリに配布します。

- Docker Hub: `dnomd343/syncplay`
- Github Package: `ghcr.io/dnomd343/syncplay`
- Tencent Cloud: `ccr.ccs.tencentyun.com/dnomd343/syncplay`

サポートされている CPU アーキテクチャは以下の4種類です：`amd64` 、`arm64` 、`i386` および `arm/v7`。イメージをプルすると、コンテナツールはホストアーキテクチャに基づいて適切なバージョンを自動的に選択します。

元の OCI イメージをプルし、オフライン使用のために tar ファイルとして保存できます。この目的に適しているのは [skopeo](https://github.com/containers/skopeo.git) ツールを使用することです。

> `docker save` コマンドを使用してイメージをエクスポートすることもできますが、単一のアーキテクチャのみをサポートします。

```bash
# バージョン 1.7.5 のすべてのアーキテクチャのイメージをアーカイブします。
$ skopeo copy --all                             \
    docker://docker.io/dnomd343/syncplay:v1.7.5 \
    oci-archive:syncplay-v1.7.5.tar

# バージョン 1.7.5 の `arm64` アーキテクチャのイメージをアーカイブします。
$ skopeo copy --override-os=linux --override-arch=arm64 \
    docker://docker.io/dnomd343/syncplay:v1.7.5         \
    oci-archive:syncplay-v1.7.5-arm64.tar

# 別のコンピュータに移動し、docker 用に抽出します。
$ docker load < syncplay-v1.7.5.tar
```

## トラブルシューティング

エラーが発生した場合は、まず `docker logs syncplay` コマンドを使用してプロセス出力を確認してください。有用なエラー情報が含まれている場合があります。さらに、環境変数 `DEBUG=ON` を設定することで、詳細なログを有効にすることもできます。

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

## 高度な設定

さまざまな理由から、構成ファイルや作業ディレクトリのパスを変更する必要がある場合があります。Syncplay コンテナでは、環境変数を使用してそれを指定する必要があります。

+ `TEMP_DIR` ：一時ディレクトリ。永続化する必要はなく、デフォルトは `/tmp/` です。
+ `WORK_DIR` ：Syncplay に関連するデータを格納する作業ディレクトリ。デフォルトは `/data/` です。
+ `CERT_DIR` ：TLS 証明書およびプライベートキーを保存するための証明書ディレクトリ。デフォルトは `/certs/` です。

## イメージのビルド

> このプロジェクトは、そのビルド中にいくつかの [BuildKit](https://github.com/moby/buildkit.git) 機能を利用しています（Docker 23.0 以降にバンドル）。そのため、他のビルドツールは互換性の問題が発生する場合があります。

以下のコマンドを使用して、ソースコードから直接イメージをビルドできます。

```bash
$ docker build -t syncplay https://github.com/dnomd343/syncplay-docker.git
```

ソースコードを修正して独自のカスタマイズを実装することもできます。

```bash
$ git clone https://github.com/dnomd343/syncplay-docker.git

$ cd ./syncplay-docker/
# いくつかの編集...

$ docker build -t syncplay .
```

複数のアーキテクチャ用のイメージが必要な場合は、`buildx` コマンドを使用してビルドする必要があります。

```bash
$ docker buildx build -t dnomd343/syncplay                    \
    --platform=linux/amd64,linux/386,linux/arm64,linux/arm/v7 \
    https://github.com/dnomd343/syncplay-docker.git --push
```

## ライセンス

MIT License ©2026 [@dnomd343](https://github.com/dnomd343)
