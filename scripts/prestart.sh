set -e
set -x

python app/backend_pre_start.py

alembic upgrade head

python app/initial_data.py

mkdir -p app/core/certs

PRIVATE_KEY="app/core/certs/private_key.pem"
PUBLIC_KEY="app/core/certs/public_key.pem"


if [ ! -f "$PRIVATE_KEY" ]; then
    openssl genrsa -out "$PRIVATE_KEY" 2048
fi


if [ ! -f "$PUBLIC_KEY" ]; then
    openssl rsa -in "$PRIVATE_KEY" -outform PEM -pubout -out "$PUBLIC_KEY"
fi