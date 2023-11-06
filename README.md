## Quick Start

[简体中文](./README_zh-CN.md)

Using one command to start the Syncplay service. Yes, it's very simple.

```bash
> docker run --rm --net=host dnomd343/syncplay
Welcome to Syncplay server, ver. 1.7.0
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
docker run -d --net=host           \
  --restart=always --name=syncplay \
  dnomd343/syncplay --disable-chat \
  --password=PASSWD --motd='HELLO WORLD'
```

The server will be restarted when necessary, or the Docker service or Syncplay may need to be updated. Whether it is expected or not, it is necessary to persist Syncplay at this time, which means that the room data will be saved to disk. You need to choose a working directory to save them, such as `/etc/syncplay/` , execute the following command, the data will be saved to the `rooms.db` file.

```bash
docker run -d --net=host           \
  --restart=always --name=syncplay \
  --volume /etc/syncplay/:/data/   \
  dnomd343/syncplay --persistent
```

This directory has more uses. For example, adding the `--enable-stats` option will enable the statistics function, and the data will be saved to the file `stats.db` in the directory. You can also create a `config.yml` file in the directory and write the configuration parameters in it, Syncplay will automatically read it when it starts, avoiding the need to type a large number of parameters in the command line.

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

+ `--salt [SALT]` ：A string used to secure passwords (e.g. Rainbow-tables), defaults to empty.

+ `--random-salt` ：Use a randomly generated salt value, valid when `--salt` is not specified, not enabled by default.

+ `--isolate-rooms` ：Room isolation enabled, users will not be able to see information from anyone other than their own room, not enabled by default.

+ `--disable-chat` ：Disables the chat feature, not enabled by default.

+ `--disable-ready` ：Disables the readiness indicator feature, not enabled by default.

+ `--enable-stats` ：Enable the server statistics feature, the data will be saved in the `stats.db` file, not enabled by default.

+ `--enable-tls` ：Enable TLS support, the certificate file needs to be mounted in the `/certs/` directory, including `cert.pem` , `chain.pem` and `privkey.pem` , not enabled by default.

+ `--persistent` ：Enable room data persistence, the information will be saved to the `rooms.db` file, only valid when `--isolate-rooms` is not specified, not enabled by default.

+ `--max-username [N]` ：Maximum length of usernames, default is `150` .

+ `--max-chat-message [N]` ：Maximum length of chat messages, default is `150` .

+ `--permanent-rooms [ROOM ...]` ：Specifies a list of rooms that will still be listed even if their playlist is empty, only valid when `--persistent` is specified, defaults to empty.

You can also use the following command to output help information.

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

## Configure File

If you configure a lot of options, it will be quite troublesome and error-prone to enter a large number of command line parameters every time you start. At this time, you can write them into the configuration file. Create a `config.yml` file in the working directory. It uses YAML format and supports all parameters in the command line. Syncplay will automatically read and load it when starting, but it should be noted that if the same parameters are specified on the command line, will override the configuration file's options.

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
syncplay    | Welcome to Syncplay server, ver. 1.7.0
```

> Adding the `-d` option allows the service to run in the background.

Similarly, you can map the certificate directory to enable TLS functionality, and edit the `config.yml` file to configure more options.

## Troubleshooting

If you encounter any errors, please first use the `docker logs syncplay` command to print the process output. It may contain useful error information. You can also output more detailed logs by specifying the environment variable `DEBUG=ON` .

```bash
> docker run --rm --env DEBUG=ON dnomd343/syncplay
Command line arguments -> Namespace(port=None, password=None, motd=None, salt=None, random_salt=False, isolate_rooms=False, disable_chat=False, disable_ready=False, enable_stats=False, enable_tls=False, persistent=False, max_username=None, max_chat_message=None, permanent_rooms=None)
Parsed arguments -> {}
Syncplay startup arguments -> ['--port', '8999', '--salt', '']
Welcome to Syncplay server, ver. 1.7.0
```

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

MIT ©2022 [@dnomd343](https://github.com/dnomd343)
