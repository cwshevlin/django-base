# django-base

An opinionated Django starter: Postgres + Docker Compose, DRF at `api/v1/` with JWT auth, Resend email via Anymail, WhiteNoise static serving, auditlog history, and a custom user model.

## What's included

- **Django 6 on Python 3.14** — 3.14 is required; model primary keys use the stdlib `uuid.uuid7`
- **Postgres 17** via Docker Compose, credentials via Docker secrets (`_read_secret()` in settings reads `<NAME>_FILE` or falls back to the plain env var)
- **Custom user model** (`authn.User`) with `email_verified` / `avatar_url` / `phone_number`, plus a signed-token email-verification flow shared by the web and API
- **DRF at `api/v1/`** (package per resource) with SimpleJWT (60-min access, 90-day rotating refresh) + session auth; interactive docs at `/api/schema/swagger-ui/` and `/api/schema/redoc/`
- **Email via Resend** (`django-anymail`); console backend whenever `DEBUG=1`
- **WhiteNoise** compressed-manifest static files, collected on container boot
- **django-auditlog** change history, browsable at `/history/<app>/<model>/<pk>/`
- **Model conventions** in `config/models.py`: `UUIDTimeStampedModel` (uuid7 PK + timestamps) and `BaseModel` (adds soft delete)
- **pytest + coverage**, black, pylint

## Quickstart (Docker)

1. Create the three secret files (gitignored):

   ```
   python3 -c "import secrets; print(secrets.token_urlsafe(50))" > secret_key.txt
   echo "postgres" > db_password.txt
   echo "re_your_resend_key" > email_api_key.txt
   ```

2. Build and start everything (the entrypoint runs collectstatic, migrate, and an optional `SEED_DB=1`-gated fixture load):

   ```
   docker compose up --build
   ```

3. Create an admin user:

   ```
   docker compose exec backend python manage.py createsuperuser
   ```

4. Visit http://localhost:8003 — the site; `/admin/` — Django admin; `/api/schema/swagger-ui/` — API docs. (The host port is `8003` in `docker-compose.yaml`; pick a unique one per project and point Caddy/the tunnel at it.)

## Local development (venv)

Requires Python ≥ 3.14.

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
docker compose up -d database
export DEBUG=1 POSTGRES_HOST=localhost
python manage.py migrate
python manage.py runserver
```

In DEBUG mode, `SECRET_KEY`, the database password, and the Resend key fall back to development defaults, and email prints to the console.

## Tests

```
docker compose exec backend pytest              # inside Docker
DEBUG=1 POSTGRES_HOST=localhost pytest          # local venv (database service must be running)
```

Coverage is reported automatically (`--cov` is in `pytest.ini`).

## Formatting and linting

```
black .
pylint authn api config
```

## Going to production

- Set `DEBUG: "0"` in `docker-compose.yaml` — all three secrets then become required at startup
- Add your hostname to `ALLOWED_HOSTS` and `https://your-domain` to `CSRF_TRUSTED_ORIGINS` in `config/settings.py`
- Set `DEFAULT_FROM_EMAIL` to a sender on your verified Resend domain
- The stack expects HTTPS terminated at the Cloudflare edge (cloudflared tunnel → Caddy → localhost:8000); `SECURE_PROXY_SSL_HEADER` is preconfigured for this

## Conventions

- New domain models extend `config.models.BaseModel`; query live rows with `Model.objects.alive()`; `delete()` soft-deletes (sets `deleted_at`), `hard_delete()` really deletes
- New API resources live at `api/v1/<resource>/` with their own `serializers.py` / `views.py` / `urls.py`, included from `api/v1/urls.py`; shared pagination and object permissions live in `api/v1/pagination.py` and `api/v1/permissions.py`
- Register models with `auditlog.register(...)` (see `authn/models.py`) to get history in admin and at `/history/<app>/<model>/<pk>/`
- Each app can ship a `fixtures/seed.json` loaded by the entrypoint when `SEED_DB=1`
