# Profile Intelligence Service

A Django REST API that enriches names using external APIs (Genderize, Agify, Nationalize) and stores the results.

## Endpoints

- `POST /api/profiles/` - Create a profile
- `GET /api/profiles/` - List all profiles
- `GET /api/profiles/{id}/` - Get a profile by ID
- `DELETE /api/profiles/{id}/` - Delete a profile

## Setup

1. Clone the repo
2. Create a virtual environment and activate it
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables (see `.env.example`)
5. Run migrations: `python manage.py migrate`
6. Start server: `python manage.py runserver`