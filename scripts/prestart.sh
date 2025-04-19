#!/usr/bin/env bash

set -e
set -x

mkdir -p app/core/certs

PRIVATE_KEY="app/core/certs/private_key.pem"
PUBLIC_KEY="app/core/certs/public_key.pem"


if [ ! -f "$PRIVATE_KEY" ]; then
    echo "Generating private key..."
    openssl genrsa -out "$PRIVATE_KEY" 2048
else
    echo "Private key already exists."
fi

if [ ! -f "$PUBLIC_KEY" ]; then
    echo "Generating public key..."
    openssl rsa -in "$PRIVATE_KEY" -outform PEM -pubout -out "$PUBLIC_KEY"
else
    echo "Public key already exists."
fi

python -m app.backend_pre_start

alembic upgrade head

python -m app.initial_data

exec "$@"