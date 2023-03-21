## Quick Start

Start a syncplay service at `tcp/8999` with one command.

```bash
docker run -d --network host --name syncplay dnomd343/syncplay
```

More arguments can be specified.

```bash
docker run -d --network host --name syncplay dnomd343/syncplay \
  --port 12345 --password dnomd343 --motd hello --isolate-room --disable-chat
```

You can also use environment variables to specify.

```bash
docker run -d --network host --name syncplay \
  --env PORT=12345 \
  --env PASSWD=dnomd343 \
  dnomd343/syncplay
```

Enable TLS support of Syncplay server.

```bash
docker run -d --network host --name syncplay \
  --volume /etc/ssl/certs/343.re/:/certs/ dnomd343/syncplay --enable-tls
```

> The `/etc/ssl/certs/343.re/` folder stores certificates and private key files, and specific introductions and examples will be given below.

### Options

You can specify the following arguments:

+ `--port [PORT]` ：Listening port of Syncplay server, the default is `8999`.

+ `--motd [MESSAGE]` ：The welcome text after the user enters the room.

+ `--password [PASSWD]` ：Authentication when the user connects to the syncplay server.

+ `--salt [SALT]` ：A string used to secure passwords (e.g. Rainbow-tables), defaults to empty.

+ `--random-salt` ：Use a randomly generated salt value, valid when `--salt` is not specified.

+ `--isolate-room` ：Room isolation enabled, users will not be able to see information from anyone other than their own room.

+ `--disable-chat` ：Disables the chat feature.

+ `--disable-ready` ：Disables the readiness indicator feature.

+ `--max-username-length` ：Maximum length of usernames (number of characters).

+ `--max-chat-message-length` ：Maximum length of chat messages (number of characters).

+ `--enable-tls` ：Enable tls support, the certificate directory should be synchronized to `/certs/`, including `cert.pem`, `chain.pem` and `privkey.pem` three files.

    + `cert.pem` ：The certificate issued by the CA.
    + `chain.pem` ：The certificate chain of CA service.
    + `privkey.pem` ：The private key for the certificate.

> For example, in [`acme.sh`](https://acme.sh/), they correspond to `--cert-file`, `--ca-file` and `--key-file` respectively, the following is an example of certificate installation.

```bash
# Export the domain `343.re` to `/etc/ssl/certs/343.re/`
acme.sh --install-cert -d 343.re \
  --cert-file  /etc/ssl/certs/343.re/cert.pem \
  --ca-file    /etc/ssl/certs/343.re/chain.pem \
  --key-file   /etc/ssl/certs/343.re/privkey.pem
```

You can also specify arguments through environment variables:

+ `PORT` ：Equivalent to `--port`.

+ `SALT` ：Equivalent to `--salt`.

+ `PASSWD` ：Equivalent to `--password`.

+ `TLS=ON` ：Equivalent to `--enable-tls`.

> Note that its priority is lower than command line arguments.

### License

MIT ©2022 [@dnomd343](https://github.com/dnomd343)
