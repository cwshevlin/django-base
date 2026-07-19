#!/bin/sh
set -e

python manage.py collectstatic --noinput --clear
python manage.py migrate

# Seed data only when explicitly requested (e.g. first boot). Running this on
# every start would re-import fixtures and clobber live data.
if [ "$SEED_DB" = "1" ]; then
    python manage.py loaddata seed
fi

exec "$@"
