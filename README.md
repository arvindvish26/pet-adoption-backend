# Pet Adoption Backend (Django + DRF)

Backend for the Pet Adoption System built with Django, Django REST Framework, JWT auth, filtering, and pagination.

## Tech Stack
- Django 5
- Django REST Framework
- JWT Auth (djangorestframework-simplejwt)
- Filtering (django-filter)
- SQLite (dev)

## Prerequisites
- Python 3.12+ (works with 3.13)
- pip

## Quick Start
```bash
cd "Pet Adoption System/pet-adoption-backend"
python3 -m venv .venv
source .venv/bin/activate #this for mac and for windows use .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
API: `http://127.0.0.1:8000/`

## First-Time Setup (if no requirements.txt)
```bash
pip install Django==5.2.5 djangorestframework djangorestframework-simplejwt django-filter Pillow
pip freeze > requirements.txt
```

## Environment
- Settings: `petstore.settings`
- Debug: enabled (dev)
- DB: SQLite `db.sqlite3`
- User model: `users.User`

## Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Create Superuser
```bash
python manage.py createsuperuser
```
Admin: `http://127.0.0.1:8000/admin/`

## Auth
- JWT via SimpleJWT
- Header: `Authorization: Bearer <access_token>`

## API Docs
See `API_DOCUMENTATION.md` for endpoints and examples.
Base: `http://127.0.0.1:8000/api/`

## Useful Commands
```bash
# Run server
python manage.py runserver 0.0.0.0:8000

# Run tests
python manage.py test

# Optional lint
pip install ruff && ruff check .
```

## Common Issues
- ImageField requires Pillow:
```bash
pip install Pillow
```
- If migrations fail in dev and you accept data loss:
```bash
rm -f db.sqlite3 && python manage.py migrate
```
- 401 on protected endpoints: verify JWT header and token freshness.

## Apps
`users`, `pets`, `accessories`, `carts`, `orders`, `payments`, `addresses`

## Production Notes
- Set `DEBUG = False`, configure `ALLOWED_HOSTS`
- Use Postgres/MySQL instead of SQLite
- Serve static/media via proper storage (e.g., S3)
- Use env vars and rotate `SECRET_KEY`
