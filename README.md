## Quick Start

[简体中文](./README_zh-CN.md) | [繁體中文](./README_zh-TW.md) | [日本語](./README_ja-JP.md)

Using one command to start the [Syncplay](https://syncplay.pl/) service. Yes, it's very simple.

```bash
> docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.1
```

> Pressing `Ctrl+C` will exit the service.

If there are no accidents, you can fill in the server IP or domain name on the client for verification, the default port is `tcp/8999` . If you can't connect, please check your firewall settings.

In order to run the service better, we can use the following command to make Syncplay run in the background and keep it started.

```bash
docker run -d --net=host --restart=always --name=syncplay dnomd343/syncplay
```

> You can use `docker ps -a` to see the running service, and using `docker rm -f syncplay` to stop the service.

You can add more arguments to achieve customization. For example, we require a password when connecting to the server, prohibit chat, and display a welcome message after entering the room. Use the following commands.

> Note that before pressing Enter, you must execute `docker rm -f syncplay` to remove the original services, otherwise they will conflict.

```bash
docker run -d --net=host --restart=always --name=syncplay dnomd343/syncplay \
  --disable-chat --password=PASSWD --motd='HELLO WORLD'
```

The server will be restarted when necessary, or the Docker service may need to be updated. Whether it is expected or not, it is necessary to persist Syncplay at this time, which means that the room data will be saved to disk. You need to choose a working directory to save them, such as `/etc/syncplay/` , execute the following command, the data will be saved to the `rooms.db` file.

```bash
docker run -d --net=host           \
  --restart=always --name=syncplay \
  --volume /etc/syncplay/:/data/   \
  dnomd343/syncplay --persistent
```

This directory has more uses. For example, adding the `--enable-stats` option will enable the statistics function, and the data will be saved to the file `stats.db` in the directory. You can also create a `config.yml` file in the directory and write the configuration options in it, Syncplay will automatically read it when it starts, avoiding the need to type a large number of arguments in the command line.

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

When deploying, it's always a good idea to turn on TLS (of course it's not necessary and this step can be skipped), and luckily Syncplay makes it easy to do this. Before starting, you need to prepare a domain name and resolve its DNS to the current server. At the same time, we must have its certificate file.

Application for a certificate can be made through [`acme.sh`](https://acme.sh/) , [`certbot`](https://certbot.eff.org/) or other reasonable methods. Anyway, you will end up with a private key and a certificate, and Syncplay requires you to provide the following three files.

+ `cert.pem` ：The certificate issued by the CA.
+ `chain.pem` ：The certificate chain of CA service.
+ `privkey.pem` ：The private key for the certificate.

For example, in `acme.sh` , you can execute the command like this to save the certificate configuration of the domain name `343.re` to the `/etc/ssl/certs/343.re/` directory.

```bash
acme.sh --install-cert -d 343.re               \
  --cert-file  /etc/ssl/certs/343.re/cert.pem  \
  --ca-file    /etc/ssl/certs/343.re/chain.pem \
  --key-file   /etc/ssl/certs/343.re/privkey.pem
```

Now that we are ready, we just need to execute the following command and a more secure and private Syncplay service will be started.

```bash
docker run -d --net=host                  \
  --restart=always --name=syncplay        \
  --volume /etc/syncplay/:/data/          \
  --volume /etc/ssl/certs/343.re/:/certs/ \
  dnomd343/syncplay --persistent --enable-tls
```

> Note that the client's server address must match the certificate, otherwise the connection will fail.

It should be noted that unlike some services, Syncplay does not need to be manually restarted when the certificate is updated. It will automatically detect certificate changes and use the latest version. In addition, TLS on the Syncplay server is adaptive, which means that even older versions of clients that do not support TLS can still communicate normally, but note that security encryption will no longer take effect at this time.

## Command-line Arguments

You can customize the Syncplay server by specifying the following command line arguments.

> The following parameters are adjusted for docker and are not exactly the same as [official documentation](https://man.archlinux.org/man/extra/syncplay/syncplay-server.1). Please refer to this when using.

+ `--port [PORT]` ：Listening port of Syncplay server, the default is `8999` .

+ `--password [PASSWD]` ：Authentication when the user connects to the syncplay server, not enabled by default.

+ `--motd [MESSAGE]` ：The welcome text after the user enters the room, not enabled by default.

+ `--salt [TEXT]` ：A string used to secure passwords (e.g. Rainbow-tables), defaults to empty.

+ `--random-salt` ：Use a randomly generated salt value, valid when `--salt` is not specified, not enabled by default.

+ `--isolate-rooms` ：Room isolation enabled, users will not be able to see information from anyone other than their own room, not enabled by default.

+ `--disable-chat` ：Disables the chat feature, not enabled by default.

+ `--disable-ready` ：Disables the readiness indicator feature, not enabled by default.

+ `--enable-stats` ：Enable the server statistics feature, the data will be saved in the `stats.db` file, not enabled by default.

+ `--enable-tls` ：Enable TLS support, the certificate file needs to be mounted in the `/certs/` directory, including `cert.pem` , `chain.pem` and `privkey.pem` , not enabled by default.

+ `--persistent` ：Enable room data persistence, the information will be saved to the `rooms.db` file, only valid when `--isolate-rooms` is not specified, not enabled by default.

+ `--max-username [NUM]` ：Maximum length of usernames, default is `150` .

+ `--max-chat-message [NUM]` ：Maximum length of chat messages, default is `150` .

+ `--permanent-rooms [ROOM ...]` ：Specifies a list of rooms that will still be listed even if their playlist is empty, only valid when `--persistent` is specified, defaults to empty.

+ `--listen-ipv4` ：Customize the listening address of the Syncplay service on the IPv4 network, not enabled by default.

+ `--listen-ipv6` ：Customize the listening address of the Syncplay service on the IPv6 network, not enabled by default.

> Only when you specify `--listen-ipv4`, Syncplay will not listen on IPv6 and vice versa. When both are specified, Syncplay will work under dual-stack networking.

You can also use the following command to output help information.

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

## Configure File

If you configure a lot of options, it will be quite troublesome and error-prone to enter a large number of command line arguments every time you start. At this time, you can write them into the configuration file. Create a `config.yml` file in the working directory. It uses YAML format and supports all arguments in the command line. Syncplay will automatically read and load it when starting, but it should be noted that if the same arguments are specified on the command line, will override the configuration file's options.

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

## Environment Variables

The Syncplay container also supports configuration through environment variables. It supports three types of fields: numbers, strings, and boolean, this means that `permanent-rooms` is not supported. Environment variables are named in uppercase letters, and `-` is replaced by `_` , boolean values are represented by `ON` or `TRUE`. The following is an example of using environment variables.

```bash
docker run -d --net=host --restart=always --name=syncplay \
  --env PORT=7999 --env MOTD=Hello --env DISABLE_READY=ON \
  dnomd343/syncplay
```

You may have noticed that we support three configuration methods: command line arguments, configuration file and environment variables. Their priority is from high to low, that is, the command line arguments will override the options of the configuration file, and the configuration file will override the environment variables. You can use them together.

## Docker Compose

Using `docker-compose` to deploy Syncplay is a more elegant way. You need to create a `docker-compose.yml` configuration file and write the following example.

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

We save this file in the `/etc/syncplay/` directory. Since a relative path is used, it is also in the working directory. Execute the command in this directory to start the Syncplay service.

```bash
> docker-compose up
Recreating syncplay ... done
Attaching to syncplay
syncplay    | Welcome to Syncplay server, ver. 1.7.1
```

> Adding the `-d` option allows the service to run in the background.

Similarly, you can map the certificate directory to enable TLS functionality, and edit the `config.yml` file to configure more options.

## Troubleshooting

If you encounter any errors, please first use the `docker logs syncplay` command to print the process output. It may contain useful error information. You can also output more detailed logs by specifying the environment variable `DEBUG=ON` .

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

## Advanced

For some reason, you may need to change the path of the configuration files or working directory. This is possible in the Syncplay container, which requires you to specify it using environment variables.

+ `TEMP_DIR` ：Temporary directory, it does not need to be persisted, defaults to `/tmp/`

+ `WORK_DIR` ：The working directory, which stores data related to Syncplay, defaults to `/data/`

+ `CERT_DIR` ：Certificate directory, which is used to store TLS certificates and private key files, defaults to `/certs/`

+ `CONFIG` ：Configuration file, which defines the YAML configuration read by the bootstrap script, defaults to `config.yml`

## Build Image

You can build an image directly from the source code using the following command.

```bash
docker build -t syncplay https://github.com/dnomd343/syncplay-docker.git
```

You can also change the source code to implement your own customizations.

```bash
> git clone https://github.com/dnomd343/syncplay-docker.git
> cd syncplay-docker/
# some edit...
> docker build -t syncplay .
```

If you need images for multiple architectures, please use the `buildx` command to build.

```bash
docker buildx build -t dnomd343/syncplay                    \
  --platform=linux/amd64,linux/386,linux/arm64,linux/arm/v7 \
  https://github.com/dnomd343/syncplay-docker.git --push
```

## License

MIT ©2023 [@dnomd343](https://github.com/dnomd343)
