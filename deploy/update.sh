#!/bin/sh
# Deploys the latest main branch. Run on the server as the admin user.
set -eu

# The service cannot read home directories, so uv's Python lives next to
# the app.
export UV_PYTHON_INSTALL_DIR=/srv/portfolio/python

cd /srv/portfolio/app
git pull --ff-only
uv sync --frozen --no-dev --compile-bytecode
# Content is loaded at startup, so every change needs a restart.
sudo systemctl restart portfolio

for _ in 1 2 3 4 5 6 7 8 9 10; do
    if curl --fail --silent --header 'Host: tordenskjold.de' \
        http://127.0.0.1:8000/health >/dev/null; then
        echo "Deployed $(git rev-parse --short HEAD)"
        exit 0
    fi
    sleep 1
done

echo "Health check failed, see: journalctl -u portfolio -n 50" >&2
exit 1
