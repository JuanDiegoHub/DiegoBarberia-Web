#!/bin/bash
set -e
echo "=== Ejecutando migraciones ==="
python manage.py migrate --noinput

echo "=== Recopilando archivos estaticos ==="
python manage.py collectstatic --noinput

echo "=== Creando superusuario y grupos ==="
python create_superuser.py

echo "=== Iniciando servidor ==="
gunicorn config.wsgi --bind 0.0.0.0:$PORT
