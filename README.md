## Quick Start

Start a syncplay service, default at port tcp/8999.

```bash
docker run -d \
--net=host \
--name=syncplay \
-e PORT=<PORT> \
-e PASSWORD=<PASSWORD> \
dnomd343/syncplay
```

If TLS is enabled, you have to set hostname and certificate folder

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
