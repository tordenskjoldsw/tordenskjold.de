# Deployment

How the site runs in production: uvicorn behind nginx, managed by systemd.
Secrets and the legal texts never enter the repository; they exist only on
the server.

## Requirements

- A Linux server with systemd, nginx, certbot, git, curl and
  [uv](https://docs.astral.sh/uv/)
- An admin user with sudo, ports 80 and 443 reachable
- DNS for `tordenskjold.de` and `www.tordenskjold.de` pointing to the
  server

| Path on the server | Content | Owner, mode |
|---|---|---|
| `/srv/portfolio/app` | checkout of this repository | admin user |
| `/srv/portfolio/python` | Python installed by uv | admin user |
| `/etc/portfolio/portfolio.env` | settings, from `portfolio.env.example` | root, `0600` |
| `/etc/portfolio/legal/` | `imprint.md`, `privacy.md` | root:portfolio, `0750`/`0640` |

The app runs as the system user `portfolio`, which can read but not write
any of these.

## 1. Code

```sh
sudo install -d -o "$USER" -g "$USER" -m 755 /srv/portfolio
git clone https://github.com/tordenskjoldsw/tordenskjold.de.git /srv/portfolio/app
cd /srv/portfolio/app
```

All later commands run from `/srv/portfolio/app`.

## 2. App

The service cannot read home directories, so uv installs Python next to
the app:

```sh
sudo useradd --system --user-group --no-create-home --shell /usr/sbin/nologin portfolio
UV_PYTHON_INSTALL_DIR=/srv/portfolio/python uv sync --frozen --no-dev --compile-bytecode
```

Settings and legal texts (copy `imprint.md` and `privacy.md` to the home
directory first, for example with `scp`):

```sh
sudo install -d -m 755 /etc/portfolio
sudo install -m 600 deploy/portfolio.env.example /etc/portfolio/portfolio.env
sudo install -d -o root -g portfolio -m 750 /etc/portfolio/legal
sudo install -o root -g portfolio -m 640 ~/imprint.md ~/privacy.md /etc/portfolio/legal/
```

Service:

```sh
sudo install -m 644 deploy/systemd/portfolio.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now portfolio
curl -fsS -H 'Host: tordenskjold.de' http://127.0.0.1:8000/health
```

If the service does not start, `journalctl -u portfolio -n 50` shows why.
Errors that look like crashes rather than Python tracebacks usually come
from the sandbox; try commenting out `MemoryDenyWriteExecute` first.
`systemd-analyze security portfolio` rates the sandbox.

## 3. nginx and TLS

Disable the default site if the nginx package ships one; it claims the
default server on port 80. nginx needs a certificate before it can serve
HTTPS, so HTTP comes first:

```sh
sudo install -d /var/www/letsencrypt
sudo install -m 644 deploy/nginx/http.conf /etc/nginx/conf.d/tordenskjold.de-http.conf
sudo nginx -t && sudo systemctl reload nginx
sudo certbot certonly --webroot -w /var/www/letsencrypt \
    -d tordenskjold.de -d www.tordenskjold.de \
    --deploy-hook "systemctl reload nginx"
sudo install -d /etc/nginx/snippets
sudo install -m 644 deploy/nginx/tls.conf /etc/nginx/snippets/tordenskjold.de-tls.conf
sudo install -m 644 deploy/nginx/https.conf /etc/nginx/conf.d/tordenskjold.de-https.conf
sudo nginx -t && sudo systemctl reload nginx
sudo certbot renew --dry-run
```

## 4. Logs

The privacy policy promises that page views are not recorded and that
error logs are deleted after 7 days. nginx and the app write no access
log; errors go to the journal, which keeps entries for at most about 7
days:

```sh
sudo install -d /etc/systemd/journald.conf.d
sudo install -m 644 deploy/journald/retention.conf /etc/systemd/journald.conf.d/
sudo systemctl restart systemd-journald
```

## 5. Checks

From another machine:

```sh
curl -sI http://tordenskjold.de          # 301 to https://tordenskjold.de/
curl -sI https://www.tordenskjold.de     # 301 to https://tordenskjold.de/
curl -sI https://tordenskjold.de         # 200 with CSP and HSTS headers
curl -sI "http://$(dig +short tordenskjold.de)"   # empty reply, unknown host
```

On the server, after a few page views:

```sh
sudo ls -la /var/log/nginx/      # access.log absent or empty
journalctl -t nginx              # errors only
```

## Updates

```sh
/srv/portfolio/app/deploy/update.sh
```

It pulls, syncs dependencies, restarts the service and checks
`/health`. When a file in `deploy/` changes, install it again as above;
the update script only deploys the app.
