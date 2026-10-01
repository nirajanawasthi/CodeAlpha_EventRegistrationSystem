# CodeAlpha_EventRegistrationSystem

Event Registration System built with Django + Django REST Framework (CodeAlpha Internship, Task 2).

## Features
- Django backend with token authentication
- Models: `Event`, `Registration` (linked to users and events)
- API: event list, event details, registration form submit
- Users can view and cancel their registrations
- Admin panel + organizer (staff) permissions
- Capacity check, duplicate-registration prevention, re-register after cancel
- Single-page frontend in plain HTML, CSS and JavaScript (no framework)

## Setup
```bash
python -m venv venv
source venv/bin/activate          # Windows PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
App (frontend): http://127.0.0.1:8000/
Admin panel: http://127.0.0.1:8000/admin/

Default DB is SQLite. For PostgreSQL set env vars:
`DB_ENGINE=postgres DB_NAME=eventdb DB_USER=postgres DB_PASSWORD=... DB_HOST=localhost DB_PORT=5432`

## Sample data
Create a superuser first (the seed script assigns the events to the superuser or a staff user), then load the sample events:

```bash
# Windows PowerShell
Get-Content seed_events.py | python manage.py shell

# macOS / Linux / Git Bash
python manage.py shell < seed_events.py
```

## Organizer
In the admin panel, open a user and tick **Staff status**. Staff users can create events.

## Frontend
The UI is served at `http://127.0.0.1:8000/` and talks to the API with the Fetch API.

- Anyone can browse events. Login and Sign up are in the header.
- Users register through a form (full name, email, phone) and can cancel or register again.
- Organizers can create events, see who registered, and delete their own events.

## Design notes
- Token authentication with role-based permissions (normal user, organizer, superuser).
- Soft cancel: cancelling keeps the record and sets its status to `cancelled`.
- Capacity check and a database constraint that prevents duplicate registrations.
- Transaction + `select_for_update`, so two people registering for the last seat cannot both succeed.
- XSS protection: user text is escaped in the UI with `esc()`.

## API Endpoints (prefix `/api/`)
| Method | URL | Purpose | Auth |
|---|---|---|---|
| POST | auth/signup/ | Create user | No |
| POST | auth/login/ | Get token | No |
| GET | auth/me/ | Current user | User |
| GET | events/ | Event list | No |
| POST | events/ | Create event | Organizer |
| GET | events/{id}/ | Event details | No |
| PUT/PATCH/DELETE | events/{id}/ | Edit/delete event | Owner organizer |
| POST | events/{id}/register/ | Submit registration form | User |
| GET | events/{id}/registrations/ | See who registered | Owner organizer |
| GET | registrations/ | My registrations | User |
| GET | registrations/{id}/ | One registration | User |
| POST/DELETE | registrations/{id}/cancel/ | Cancel registration | User |

Header: `Authorization: Token <your_token>`

## Example (curl)
```bash
curl -X POST localhost:8000/api/auth/signup/ -H "Content-Type: application/json" \
  -d '{"username":"ram","email":"ram@x.com","password":"secret123"}'

curl -X POST localhost:8000/api/auth/login/ -H "Content-Type: application/json" \
  -d '{"username":"ram","password":"secret123"}'

curl -X POST localhost:8000/api/events/1/register/ \
  -H "Authorization: Token TOKEN" -H "Content-Type: application/json" \
  -d '{"full_name":"Ram Sharma","email":"ram@x.com","phone":"98XXXXXXXX"}'

curl localhost:8000/api/registrations/ -H "Authorization: Token TOKEN"
curl -X POST localhost:8000/api/registrations/1/cancel/ -H "Authorization: Token TOKEN"
```