# MentorMe

MentorMe is a mentorship platform for mentors and mentees. Mentors publish articles,
mentees ask forum questions and request mentorship, and the activities app tracks
notifications. Mentees sign up with a phone number and verify a six-digit SMS code before logging
in. Mentors sign up with email and remain inactive until an administrator manually
verifies and activates their account. Invitation gating remains a separate feature.

The project uses Django 6.1.2 and requires Python 3.12 or newer. It is tested with
Python 3.14. Dependencies, including transitive dependencies, are pinned in
`requirements.txt`; Pipenv is no longer used.

## Local development

```sh
python3.14 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp mentorme/local_settings.py.example mentorme/local_settings.py
```

Generate a secret and set `SECRET_KEY` in `mentorme/local_settings.py`:

```sh
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

The local settings use SQLite, in-memory caching, database sessions, and console
email, so PostgreSQL, Redis, Mailgun, and SMS credentials are not needed locally.
For PostgreSQL, set `DATABASE_URL` before running commands. Django 6.1 requires
PostgreSQL 15 or newer.

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`manage.py` defaults to `mentorme.local_settings`. Production WSGI defaults to
`mentorme.settings`. Use `--settings` or `DJANGO_SETTINGS_MODULE` to override this.

## Tests and checks

These commands use a disposable SQLite test database and require no external services:

```sh
python manage.py check --settings=mentorme.test_settings
python manage.py makemigrations --check --dry-run --settings=mentorme.test_settings
python manage.py test --settings=mentorme.test_settings
python -m pip check
```

The tests cover authentication, mentor article permissions, publishing and editing,
Markdown safety, forum answers and notifications, messaging, mentorship requests,
the milestone API, template compilation, and upgrading an existing database.

## Upgrading an existing deployment

1. Back up the database and uploaded media, then rehearse the upgrade against a
   copy of the production database.
2. Provision Python 3.12+ (3.14 is configured in `.python-version` and `runtime.txt`)
   and PostgreSQL 15+ if using PostgreSQL.
3. Install `requirements.txt` in a fresh virtual environment. Do not retain the old
   environment's Raven or duplicate REST Framework packages.
4. Update deployment configuration: set `SECRET_KEY`, `DATABASE_URL`, and
   comma-separated `ALLOWED_HOSTS`. `DEBUG=false` is the default. Supply Mailgun,
   Redis, and Africa's Talking credentials for the integrations you use. `SENTRY_DSN`
   replaces `SENTRY_DNS`, with the old spelling still accepted for compatibility.
5. Apply migrations and collect static files before starting the application:

   ```sh
   python manage.py migrate --settings=mentorme.settings
   python manage.py collectstatic --noinput --settings=mentorme.settings
   python manage.py check --settings=mentorme.settings
   gunicorn mentorme.wsgi
   ```

The historical migration files are retained. New migrations reconcile existing
model definitions and rename the legacy question-tag index. Integer primary keys
are preserved through `DEFAULT_AUTO_FIELD`. These migrations do not remove members
or content.

Logout now uses a CSRF-protected POST form, as required by modern Django. Static
storage uses `STORAGES`, AJAX detection uses request headers, and Markdown rendering
escapes raw HTML and sanitizes links. Raven is replaced by the maintained Sentry
SDK; Celery and the SMS integration use their current APIs. Production caching and
sessions still use Redis; Celery workers can start with `celery -A mentorme worker`.

Validation has been performed on SQLite. Verify migrations and service integration
against your deployment's PostgreSQL database, Redis, Mailgun, and SMS provider
before rollout.

## Signup and verification

Mentees enter their phone number in international format (e.g. `+254700000000`).
Signup creates an inactive account and sends a six-digit SMS through Africa's
Talking using `AFRICAS_TALKING_USERNAME` and `AFRICAS_TALKING_API_KEY`. Delivery runs
during signup, so it does not require a Celery worker. The verification page is
linked to the signup session; keep using the same browser until verification is
complete. A valid code activates the account and redirects to login.

Codes are stored as hashes, expire after 10 minutes, and allow five incorrect
attempts. Sending a replacement code requires waiting one minute and invalidates
the previous code. SMS failures keep the account inactive and show a retry option.
A working SMS provider configuration is required to complete this flow locally.

Mentors provide their email and see a pending approval page. After contacting and
verifying a mentor, an administrator can use **Users → Role: mentor → Active: No**,
select the reviewed account, and choose **Activate mentors after manual verification**.
The action only activates mentors. Users cannot change their own role during setup
or through profile settings. Apply the new verification migration before rollout:

```sh
python manage.py migrate
```
