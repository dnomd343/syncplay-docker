## Quick Start

Start a syncplay service at `tcp/8999`, you can also specify a password.

```bash
docker run -d \
--network host \
--name syncplay \
--env PORT=<PORT> \
--env PASSWORD=<PASSWORD> \
dnomd343/syncplay
```

If TLS is enabled, you have to set certificate folder with `privkey.pem`, `cert.pem` and `chain.pem`.

```bash
docker run -d \
--network host \
--name syncplay \
--env PORT=<PORT> \
--env PASSWORD=<PASSWORD> \
--env TLS=/certs \
--volume <certs>:/certs \
dnomd343/syncplay
```

You can get more information on the [official documentation](https://syncplay.pl/guide/server/).
