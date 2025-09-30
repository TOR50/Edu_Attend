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
- `ALLOWED_HOSTS` – set in `config/settings.py` for deployment

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

## License

Add a LICENSE file to clarify terms for use and distribution (e.g., MIT).

    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            # Find all faces and encodings in the current frame
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_faces, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]
                    # MARK THE STUDENT AS PRESENT IN THE DATABASE HERE
                    # You can use another request or a background task

                # ... (code to draw a box around the face and label it)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
The Template (take_attendance.html): In the HTML, you simply use an <img> tag whose source points to this streaming view.

HTML

<h3>Live Camera Feed</h3>
<img src="{% url 'video_feed' class_id=class.id %}" width="640" height="480">
💻 Part 7: Frontend Development
Use a simple, clean design. Bootstrap is excellent for this.

Create a base.html template: This will contain the main structure, including the navbar, and will be extended by all other pages.

Use Django Template Tags: Use {% extends 'base.html' %} and {% block content %} to build out individual pages.

Make it Responsive: Use Bootstrap's grid system (container, row, col-md-6, etc.) to ensure the layout adapts to different screen sizes, making it usable on phones.

Add JavaScript: For the attendance page, a little bit of JavaScript will be needed to periodically check for updates (which students have been marked present) and refresh the student list without a full page reload