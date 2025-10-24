# LAVA2 — Plataforma de Gestión de Lavado de Autos

**Estado:** WIP (Paso 1–5 completados)  
**Stack:** Python 3.12, Django 5, PostgreSQL, MVT, Docker (próximo), CI con GitHub Actions.

## Desarrollo local

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements/development.txt

# variables de entorno
cp .env.example .env   # Ajusta valores
python manage.py migrate
python manage.py runserver
