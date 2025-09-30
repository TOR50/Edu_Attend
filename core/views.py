from __future__ import annotations
import base64
import io
import json
from datetime import date
import time

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.middleware.csrf import get_token
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import CustomSignUpForm, StudentForm, FaceSampleForm, CustomLoginForm
from .models import AttendanceRecord, SchoolClass, Student, Teacher, User, FaceSample, AcademicYear

try:
    import numpy as np
    import cv2
except Exception:  # pragma: no cover - runtime import fallback
    np = None
    cv2 = None

try:
    import face_recognition  # optional
except Exception:
    face_recognition = None

from . import recognition_service

# In-memory cache for known faces per class to avoid reloading on every request
_RECOGNITION_CACHE: dict[int, dict] = {}


def _get_known_faces_for_class(class_id: int) -> tuple[list, list]:
    """
    Get known faces from cache or load them if cache is stale or missing.
    """
    now = time.time()
    entry = _RECOGNITION_CACHE.get(class_id)
    
    # Reuse cache if it's less than 30 seconds old
    if entry and now - entry.get("loaded_at", 0) < 30:
        return entry.get("known_face_encodings"), entry.get("known_face_metadata")

    # Load from service
    known_face_encodings, known_face_metadata = recognition_service.load_known_faces_for_class(class_id)
    
    _RECOGNITION_CACHE[class_id] = {
        "loaded_at": now,
        "known_face_encodings": known_face_encodings,
        "known_face_metadata": known_face_metadata,
    }
    return known_face_encodings, known_face_metadata


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")



def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("login_success")
    else:
        form = CustomSignUpForm()
    get_token(request)
    return render(request, "registration/signup.html", {"form": form})


def login_success(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore
    if not user.is_authenticated:
        return redirect("login")
    if user.role == "admin":
        return redirect("admin_dashboard")
    return redirect("teacher_dashboard")


def logout_get(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


@login_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    classes = SchoolClass.objects.all()
    students = Student.objects.select_related("school_class").all()
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added.")
            return redirect("admin_dashboard")
    else:
        form = StudentForm()
    return render(request, "admin/dashboard.html", {"classes": classes, "students": students, "form": form})


@login_required
def teacher_dashboard(request: HttpRequest) -> HttpResponse:
    # Teachers see their classes; admins see all
    if request.user.role == "teacher":  # type: ignore[attr-defined]
        teacher = Teacher.objects.filter(user=request.user).first()
        classes = teacher.classes.all() if teacher else SchoolClass.objects.none()
    else:
        classes = SchoolClass.objects.all()
    return render(request, "teacher/dashboard.html", {"classes": classes})


@login_required
def take_attendance(request: HttpRequest, class_id: int) -> HttpResponse:
    school_class = get_object_or_404(SchoolClass, id=class_id)
    
    # Get attendance records for the current date, class, and active academic year
    today = timezone.localdate()
    active_academic_year = AcademicYear.objects.filter(is_active=True).first()

    if not active_academic_year:
        # Handle case where no academic year is active
        messages.error(request, "There is no active academic year. Please set one in the admin panel.")
        return redirect('teacher_dashboard')

    # Get all students in the class
    all_students = school_class.students.all().select_related('user')

    # Get a list of student IDs who already have a 'present' record today
    present_student_ids = set(AttendanceRecord.objects.filter(
        school_class=school_class,
        date=today,
        academic_year=active_academic_year,
        status='present'
    ).values_list('student_id', flat=True))

    get_token(request)
    enc_count = sum(1 for s in all_students if s.face_encodings)

    context = {
        'school_class': school_class,
        'students': all_students,
        'present_ids': present_student_ids,
        'today': today,
        'enc_count': enc_count,
        'class': school_class, # For template compatibility
    }
    return render(request, 'teacher/take_attendance.html', context)


@login_required
def class_diagnostics(request: HttpRequest) -> JsonResponse:
    data = {
        "face_recognition_available": face_recognition is not None,
        "opencv_available": cv2 is not None,
        "numpy_available": np is not None,
        "students": [],
    }
    for s in Student.objects.select_related('user').all():
        data["students"].append({
            "id": s.pk,
            "name": s.get_full_name(),
            "has_photo": bool(s.photo),
            "has_encoding": bool(s.face_encodings),
        })
    data["total_encodings"] = sum(1 for s in Student.objects.all() if s.face_encodings)
    return JsonResponse(data)


@login_required
@require_POST
def recognize_frame(request: HttpRequest) -> JsonResponse:
    """
    Receives a video frame, runs face recognition, and returns results.
    This view also handles marking attendance in the database.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    if not all((face_recognition, cv2, np)):
        return JsonResponse({"error": "Face recognition libraries not installed"}, status=500)

    try:
        data = json.loads(request.body)
        image_data = base64.b64decode(data["image"].split(",")[1])
        class_id = data.get("class_id")
    except (json.JSONDecodeError, KeyError, IndexError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not class_id:
        return JsonResponse({"error": "class_id is required"}, status=400)

    # Convert image data to numpy array
    frame_bytes = np.frombuffer(image_data, dtype=np.uint8)
    frame = cv2.imdecode(frame_bytes, cv2.IMREAD_COLOR)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get known faces for the class
    known_face_encodings, known_face_metadata = _get_known_faces_for_class(class_id)

    # Find matches
    detections = recognition_service.find_matches_in_frame(frame_rgb, known_face_encodings, known_face_metadata)

    # Get a list of matched student IDs and their confidence
    matched_students_with_confidence = [
        (d["student_id"], 1 - d["metric"]) 
        for d in detections 
        if d["student_id"] and d["metric"] is not None
    ]
    matched_student_ids = {d[0] for d in matched_students_with_confidence}

    # Mark attendance in the database
    if matched_students_with_confidence:
        recognition_service.mark_attendance_for_matches(matched_students_with_confidence, class_id)

    return JsonResponse({
        "faces_detected": len(detections),
        "matched": list(matched_student_ids),
        "detections": detections,
        "used_face_recognition": True,
    })


@login_required
@require_POST
def mark_present(request: HttpRequest, student_id: int) -> JsonResponse:
    student = get_object_or_404(Student, pk=student_id)
    class_id = student.school_class.id if student.school_class else None
    if not class_id:
        return JsonResponse({"ok": False, "error": "Student not in a class"}, status=400)
    
    # Pass a default confidence of 1.0 for manual marking
    recognition_service.mark_attendance_for_matches([(student_id, 1.0)], class_id)
    return JsonResponse({"ok": True})


@login_required
def student_detail(request: HttpRequest, student_id: int) -> HttpResponse:
    student = get_object_or_404(Student.objects.select_related('user', 'school_class'), pk=student_id)
    if request.method == 'POST':
        form = FaceSampleForm(request.POST, request.FILES)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.student = student
            sample.save()
            messages.success(request, "Face sample uploaded successfully.")
            return redirect('student_detail', student_id=student.pk)
    else:
        form = FaceSampleForm()
        
    samples = student.samples.all().order_by('-created_at')
    return render(request, 'admin/student_detail.html', {'student': student, 'form': form, 'samples': samples})


@login_required
@require_POST
def delete_face_sample(request: HttpRequest, sample_id: int) -> HttpResponse:
    sample = get_object_or_404(FaceSample, id=sample_id)
    student_id = sample.student.pk
    # You might want to add a check here to ensure the user has permission to delete
    sample.delete()
    messages.success(request, "Face sample deleted.")
    return redirect('student_detail', student_id=student_id)