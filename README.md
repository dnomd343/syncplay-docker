## Quick Start

Start a syncplay service, default at `tcp/8999`, you can also specify a password.

```bash
docker run -d \
--net=host \
--name=syncplay \
-e PORT=<PORT> \
-e PASSWORD=<PASSWORD> \
dnomd343/syncplay
```

If TLS is enabled, you have to set hostname and certificate folder.

```bash
docker run -d \
--net=host \
--name=syncplay \
--hostname=syncplay.your.domain
-e PORT=<PORT> \
-e PASSWORD=<PASSWORD> \
-e TLS=/certs \
-v <certs>:/certs \
dnomd343/syncplay
```

You can get more information on the [official documentation](https://syncplay.pl/guide/server/).
