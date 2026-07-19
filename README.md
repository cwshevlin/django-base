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

## Decisions

These choices were mined from bike-maps (the first project to outgrow the old template) and reviewed one-by-one in July 2026.

| Decision | Rationale |
|---|---|
| Postgres 17 in Docker, psycopg 3 | Same engine in dev and prod; psycopg 3 is Django 6's preferred driver and its binary wheel needs no system libs |
| Full compose (gunicorn + db) with Docker secrets | One `docker compose up` runs the real stack; `_read_secret()` reads `<NAME>_FILE` with env-var fallback |
| Resend via Anymail, console when DEBUG | Anymail keeps `send_mail()`/password-reset untouched; bike-maps had the resend SDK installed but never wired |
| WhiteNoise manifest statics | No separate static server behind the Cloudflare tunnel; hashed filenames give cache-busting for free |
| DRF at versioned `api/v1/`, package per resource | Versioning is free from day one; each resource owns its serializers/views/urls |
| SimpleJWT (60-min access, 90-day rotating refresh) + session auth | JWT for iOS/Android clients, sessions for the browsable API |
| drf-spectacular | Swagger/Redoc docs the mobile clients actually use (must be named `SPECTACULAR_SETTINGS` — the `DRF_`-prefixed name is silently ignored) |
| UUIDv7 PKs, `created_at`/`updated_at`, soft delete | Time-ordered non-guessable IDs (stdlib `uuid.uuid7`, hence Python ≥ 3.14); `objects` is unfiltered — `.alive()` is explicit |
| `authn` app name for the custom user | `auth` collides with `django.contrib.auth`'s app label (the old template's user model never actually worked) |
| django-auditlog + `/history/…` view | Change history in admin and on-site; excludes `password`/`last_login` from logs |
| Env-driven `DEBUG`, single flat `settings.py`, raw `os.environ` | Secrets hard-fail in prod, fall back in dev; no django-environ dependency |
| Host port is per-project (8003 here) | Every project on this box publishes its own port for Caddy/the tunnel; 8000 belongs to bike-maps |
| black + pylint + pytest with coverage | House toolchain; pylint without pylint-django flags a few known Django false positives |

**Deliberately left out** (add per-project when needed): django-filter and API throttling defaults, django-cors-headers, phone/OTP auth (Twilio), Pico CSS / design tokens, dark-mode toggle, a shared `Visibility` enum. The frontend ships only a minimal `base.html` and the `message_box` tag.

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
