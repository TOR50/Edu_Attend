# Edu Attend — Face Recognition Attendance (Django)

Edu Attend is a Django web app that helps schools record attendance. Teachers can take attendance from a webcam; admins manage classes, students, and teachers. Face recognition is optional and can be enabled when supported on the host system.

## Highlights

- Custom user model with roles (admin, teacher, student)
- Manage academic years, classes (grade/section), teachers, and students
- Upload a main photo plus multiple face samples per student
- Live “Take Attendance” page; recognized students are marked present automatically
- Manual “Mark present” endpoint for cases without recognition
- Simple diagnostics endpoint to verify runtime libraries and data

## Tech stack

- Django 5 (SQLite by default)
- Pillow, NumPy
- OpenCV (frame decoding)
- Optional: face_recognition (dlib) for face encoding/matching

## Project structure (top-level)

- `config/` – Django project, settings and URLs
- `core/` – app with models, views, forms, templates, static assets
- `media/` – user uploads (students photos, face samples)
- `templates/` – base and auth templates
- `requirements.txt` – Python dependencies

## Prerequisites

- Python 3.12 or 3.13
- Windows users enabling face recognition: install CMake and Microsoft C++ Build Tools

## Quick start (Windows PowerShell)

```powershell
# 1) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install required packages
pip install -r requirements.txt

# Optional: enable face recognition (requires CMake + MSVC build tools)
# pip install dlib face_recognition

# 3) Initialize the database
python manage.py makemigrations ; python manage.py migrate

# 4) Create an admin user
python manage.py createsuperuser

# 5) Run the development server
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

## Configuration

Environment variables (recommended for production):

- `DJANGO_SECRET_KEY` – overrides the default dev key
- `DJANGO_ALLOWED_HOSTS` – comma-separated list mapped to `ALLOWED_HOSTS`
- `DJANGO_DEBUG` – set to `false` in production
- `DJANGO_CSRF_TRUSTED_ORIGINS` – comma-separated origins for HTTPS deployments

## Academic year setup

1. Sign in as an admin and open the Django admin (`/admin/`).
2. Create one or more `AcademicYear` entries (e.g., `2025-2026`).
3. Mark exactly one year as active by checking the **Is active** box—this drives attendance snapshots.
4. Update classes to point to the currently active academic year if you import legacy data.

## Assigning teachers to classes

1. From the admin dashboard, create teacher user accounts (role = teacher).
2. In the Django admin, open each teacher record and add them to the appropriate classes via the many-to-many selector.
3. Teachers only see the classes assigned here; verify assignments whenever classes change grades or sections.

## Production deployment notes

- Set the environment variables listed above before starting the app.
- Configure a persistent database and update `DATABASE_URL` or adjust `DATABASES` in `config/settings.py` accordingly.
- Collect static assets (e.g., `python manage.py collectstatic`) and serve them via WhiteNoise or your web server.
- Define `MEDIA_ROOT` storage (S3, Azure Blob, etc.) and grant write permissions so student photos are retained.
- Run `python manage.py createsuperuser` in the production environment to seed the first admin.

Static and media:

- Static files are in `core/static/` (served automatically in DEBUG)
- Uploads are stored under `media/` and served in DEBUG via `MEDIA_URL`

## Default URLs

- Home: `/`
- Auth: `/accounts/login/`, `/accounts/signup/`, `/accounts/logout/`
- Admin site: `/admin/`
- Admin dashboard: `/core/admin/dashboard/`
- Teacher dashboard: `/core/teacher/dashboard/`
- Take attendance: `/core/teacher/class/<id>/take/`
- APIs:
  - POST `/core/api/recognize/` – process one frame (base64 image) for matches
  - POST `/core/api/mark-present/<student_id>/` – mark a student present
  - GET `/core/api/diagnostics/` – library/data health check

## Face recognition notes

- The app runs without `face_recognition`; you can still use manual marking.
- To enable automatic recognition: install `dlib` and `face_recognition`, then upload clear frontal face images. Multiple samples per student improve accuracy.

## Troubleshooting

- Camera access: allow the browser to use the webcam for `localhost`.
- Missing libraries: the diagnostics endpoint reports availability of NumPy/OpenCV/face_recognition.
- Build issues on Windows: install CMake and Visual C++ Build Tools before `pip install dlib face_recognition`.

## Contributing

Small fixes and improvements are welcome. Please open an issue or a PR with a clear description and minimal repro.

