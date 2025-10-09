from __future__ import annotations
import base64
import io
import json
from datetime import date
from django.urls import reverse
import time

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.middleware.csrf import get_token
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from django.db.models import Prefetch

from .forms import CustomSignUpForm, StudentForm, FaceSampleForm, CustomLoginForm
from .models import AttendanceRecord, SchoolClass, Student, Teacher, User, FaceSample, AcademicYear, ManualExcuseLog

from PIL import Image
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


def _classes_for_user(user: User):
    role = getattr(user, "role", None)
    if role == "admin":
        return SchoolClass.objects.select_related("academic_year").all()
    if role == "teacher":
        teacher = (
            Teacher.objects.select_related("user")
            .prefetch_related(Prefetch("classes", queryset=SchoolClass.objects.select_related("academic_year")))
            .filter(user=user)
            .first()
        )
        return teacher.classes.all() if teacher else SchoolClass.objects.none()
    if role == "student":
        return SchoolClass.objects.filter(students__user=user).select_related("academic_year")
    return SchoolClass.objects.none()


def _user_can_access_class(user: User, school_class: SchoolClass) -> bool:
    role = getattr(user, "role", None)
    if role == "admin":
        return True
    if role == "teacher":
        return Teacher.objects.filter(user=user, classes=school_class).exists()
    if role == "student":
        return school_class.students.filter(user=user).exists()
    return False


def _attendance_snapshot(school_class: SchoolClass, target_date: date) -> list[dict]:
    students = list(
        school_class.students.select_related("user").order_by("roll_number", "user__first_name", "user__last_name")
    )
    records = {
        record.student_id: record
        for record in AttendanceRecord.objects.filter(
            school_class=school_class,
            date=target_date,
            academic_year=school_class.academic_year,
        ).select_related("student__user")
    }
    snapshot = []
    for student in students:
        record = records.get(student.pk)
        status = record.status if record else "absent"
        snapshot.append(
            {
                "id": student.pk,
                "name": student.get_full_name(),
                "roll_number": student.roll_number,
                "status": status,
                "confidence": getattr(record, "confidence", None),
                "photo_url": student.photo.url if student.photo else None,
            }
        )
    return snapshot


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
    if request.user.is_authenticated:
        return redirect("login_success")
    return redirect("login")



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
    role = getattr(user, "role", None)
    if role == "admin":
        return redirect("admin_dashboard")
    if role == "teacher":
        return redirect("teacher_dashboard")
    if role == "student":
        return redirect("student_dashboard")
    return redirect("home")


def logout_get(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


def _status_breakdown(snapshot: list[dict]) -> dict[str, int]:
    summary: dict[str, int] = {"present": 0, "absent": 0, "late": 0, "excused": 0}
    for entry in snapshot:
        status = entry.get("status") or "absent"
        if status not in summary:
            summary[status] = 0
        summary[status] += 1
    summary["total"] = len(snapshot)
    return summary


@login_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    if getattr(request.user, "role", None) != "admin":
        return HttpResponseForbidden("Admins only")
    classes_qs = (
        SchoolClass.objects.select_related("academic_year")
        .prefetch_related(
            Prefetch(
                "students",
                queryset=Student.objects.select_related("user"),
            )
        )
    )
    students_qs = Student.objects.select_related("school_class", "user").order_by("-user__date_joined")
    classes = list(classes_qs)
    students = list(students_qs)
    for school_class in classes:
        related_students = list(school_class.students.all())
        school_class.cached_student_total = len(related_students)
        school_class.cached_photo_total = sum(1 for s in related_students if s.photo)
        school_class.cached_encoding_total = sum(1 for s in related_students if s.face_encodings)
    academic_years = list(AcademicYear.objects.all().order_by("-is_active", "-year"))
    active_years_count = sum(1 for year in academic_years if year.is_active)
    students_with_encodings = sum(1 for s in students if s.face_encodings)
    students_with_photos = sum(1 for s in students if s.photo)
    class_count = len(classes)
    student_count = len(students)
    average_class_size = round(student_count / class_count, 1) if class_count else 0
    encoding_percent = round((students_with_encodings / student_count) * 100) if student_count else 0
    photo_percent = round((students_with_photos / student_count) * 100) if student_count else 0
    class_insights = []
    admin_root = reverse("admin:index")
    manage_roster_base = reverse("admin_students")
    for school_class in classes:
        total = school_class.cached_student_total
        encoded = school_class.cached_encoding_total
        photos = school_class.cached_photo_total
        readiness = round((encoded / total) * 100) if total else 0
        photo_ratio = round((photos / total) * 100) if total else 0
        class_insights.append(
            {
                "id": school_class.id,
                "label": f"Class {school_class.grade}-{school_class.section}",
                "year": school_class.academic_year,
                "students": total,
                "readiness": readiness,
                "photo_percent": photo_ratio,
                "admin_url": f"{admin_root}core/schoolclass/{school_class.id}/change/",
                "manage_url": f"{manage_roster_base}?class={school_class.id}",
            }
        )

    prioritized_classes = sorted(
        class_insights,
        key=lambda entry: (entry["readiness"], -entry["students"]),
    )[:5]

    recent_students_raw = students[:5]
    recent_students: list[dict] = []
    for stu in recent_students_raw:
        sid = stu.pk or None
        class_label = None
        class_year = None
        if stu.school_class:
            class_label = f"Class {stu.school_class.grade}-{stu.school_class.section}"
            class_year = str(stu.school_class.academic_year)
        profile_url = None
        if sid:
            try:
                profile_url = reverse("student_detail", args=[sid])
            except Exception:
                profile_url = None
        display_name = stu.get_full_name() or stu.user.username or "Unknown"
        photo_url: str | None = None
        has_photo = False
        photo = getattr(stu, "photo", None)
        if photo:
            try:
                photo_name = getattr(photo, "name", "")
                if photo_name and photo.storage.exists(photo_name):
                    photo_url = photo.url
                    has_photo = True
            except Exception:
                photo_url = None
                has_photo = False
        recent_students.append(
            {
                "id": sid,
                "name": display_name,
                "initial": display_name[:1].upper(),
                "photo_url": photo_url,
                "has_photo": has_photo,
                "face_ready": bool(getattr(stu, "face_encodings", None)),
                "class_label": class_label,
                "class_year": class_year,
                "profile_url": profile_url,
            }
        )

    context = {
        "classes": classes,
        "class_insights": prioritized_classes,
        "academic_years": academic_years,
    "recent_students": recent_students,
        "stats": {
            "academic_years": len(academic_years),
            "active_years": active_years_count,
            "class_count": class_count,
            "student_count": student_count,
            "encoded_students": students_with_encodings,
            "photo_students": students_with_photos,
            "average_class_size": average_class_size,
            "encoding_percent": encoding_percent,
            "photo_percent": photo_percent,
        },
    }
    return render(request, "admin/dashboard.html", context)



@login_required
def admin_students(request: HttpRequest) -> HttpResponse:
    if getattr(request.user, "role", None) != "admin":
        return HttpResponseForbidden("Admins only")

    classes = list(
        SchoolClass.objects.select_related("academic_year")
        .annotate(student_total=models.Count("students"))
        .order_by("academic_year__year", "grade", "section")
    )
    students_qs = (
        Student.objects.select_related("school_class", "user", "school_class__academic_year")
        .order_by("user__first_name", "user__last_name")
    )
    students = list(students_qs)

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"{student.get_full_name()} added successfully.")
            return redirect("admin_students")
        messages.error(request, "Please review the highlighted errors and try again.")
    else:
        form = StudentForm()

    student_count = len(students)
    encoded_count = sum(1 for s in students if s.face_encodings)
    photo_count = sum(1 for s in students if s.photo)
    class_count = len(classes)
    average_class_size = round(student_count / class_count, 1) if class_count else 0

    admin_root = reverse("admin:index")
    student_rows: list[dict] = []

    for student in students:
        full_name = student.get_full_name()
        initials_source = full_name or student.user.username
        initials = "".join(part[0].upper() for part in initials_source.split() if part)[:2]
        if not initials:
            initials = (student.user.username or "?")[:2].upper()

        class_label = "Unassigned"
        class_id = None
        class_year = None
        if student.school_class:
            class_id = student.school_class.id
            class_year = str(student.school_class.academic_year)
            class_label = f"Class {student.school_class.grade}-{student.school_class.section}"

        student_rows.append(
            {
                "id": student.pk,
                "name": full_name,
                "email": student.user.email,
                "class_label": class_label,
                "class_id": class_id,
                "class_year": class_year,
                "roll_number": student.roll_number,
                "photo_url": student.photo.url if student.photo else None,
                "initials": initials,
                "has_photo": bool(student.photo),
                "face_ready": bool(student.face_encodings),
                "manage_url": reverse("student_detail", args=[student.pk]) if student.pk else None,
                "admin_change_url": f"{admin_root}core/student/{student.pk}/change/",
                "admin_delete_url": f"{admin_root}core/student/{student.pk}/delete/",
            }
        )

    class_options = [
        {
            "id": school_class.id,
            "label": f"Class {school_class.grade}-{school_class.section}",
            "year": str(school_class.academic_year),
        }
        for school_class in classes
    ]

    context = {
        "form": form,
        "student_rows": student_rows,
        "class_options": class_options,
        "stats": {
            "student_count": student_count,
            "encoded_students": encoded_count,
            "photo_students": photo_count,
            "class_count": class_count,
            "average_class_size": average_class_size,
        },
    }
    return render(request, "admin/students.html", context)

@login_required
def teacher_dashboard(request: HttpRequest) -> HttpResponse:
    role = getattr(request.user, "role", None)
    if role not in {"teacher", "admin"}:
        return HttpResponseForbidden("Teachers only")
    classes = _classes_for_user(request.user)
    return render(request, "teacher/dashboard.html", {"classes": classes})


@login_required
def take_attendance_entry(request: HttpRequest) -> HttpResponse:
    role = getattr(request.user, "role", None)
    if role not in {"teacher", "admin"}:
        return HttpResponseForbidden("Teachers only")

    classes = list(_classes_for_user(request.user))
    target_class_id = request.GET.get("class_id")

    if target_class_id:
        try:
            target_class_id_int = int(target_class_id)
        except (TypeError, ValueError):
            target_class_id_int = None
        else:
            if any(c.id == target_class_id_int for c in classes):
                return redirect("take_attendance", class_id=target_class_id_int)

    if classes:
        last_class_id = request.session.get("last_take_attendance_class_id")
        if last_class_id is not None:
            try:
                last_class_id_int = int(last_class_id)
            except (TypeError, ValueError):
                last_class_id_int = None
            else:
                if any(c.id == last_class_id_int for c in classes):
                    return redirect("take_attendance", class_id=last_class_id_int)

    if classes:
        return redirect("take_attendance", class_id=classes[0].id)

    messages.info(request, "No classes assigned yet. Please contact an administrator." )
    return redirect("teacher_dashboard")


@login_required
def take_attendance(request: HttpRequest, class_id: int) -> HttpResponse:
    school_class = get_object_or_404(SchoolClass, id=class_id)
    if not _user_can_access_class(request.user, school_class):
        return HttpResponseForbidden("You do not have access to this class")
    
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
    classes_for_user = list(_classes_for_user(request.user))
    snapshot = _attendance_snapshot(school_class, today)
    status_summary = _status_breakdown(snapshot)

    request.session["last_take_attendance_class_id"] = school_class.id

    context = {
        'school_class': school_class,
        'students': all_students,
        'present_ids': present_student_ids,
        'today': today,
        'enc_count': enc_count,
        'class': school_class,
        'classes': classes_for_user,
        'snapshot': snapshot,
        'status_summary': status_summary,
    }
    return render(request, 'teacher/take_attendance.html', context)


@login_required
def attendance_overview(request: HttpRequest) -> HttpResponse:
    role = getattr(request.user, "role", None)
    if role not in {"teacher", "admin"}:
        return HttpResponseForbidden("Teachers only")

    classes = list(_classes_for_user(request.user))
    selected_class = None

    if classes:
        requested_class_id = request.GET.get("class_id")
        if requested_class_id:
            try:
                requested_class_id = int(requested_class_id)
            except (TypeError, ValueError):
                requested_class_id = None
        else:
            requested_class_id = None

        if requested_class_id is not None:
            selected_class = next((c for c in classes if c.id == requested_class_id), None)
            if selected_class is None:
                return HttpResponseForbidden("You do not have access to this class")
        if selected_class is None:
            selected_class = classes[0]

    date_param = request.GET.get("date")
    selected_date = timezone.localdate()
    if date_param:
        try:
            selected_date = date.fromisoformat(date_param)
        except ValueError:
            pass

    snapshot = _attendance_snapshot(selected_class, selected_date) if selected_class else []
    status_summary = _status_breakdown(snapshot) if selected_class else {"present": 0, "absent": 0, "late": 0, "excused": 0, "total": 0}

    student_roster = []
    if selected_class:
        student_roster = [
            {
                "id": student.pk,
                "name": student.get_full_name(),
                "roll_number": student.roll_number,
            }
            for student in selected_class.students.select_related("user").order_by("roll_number", "user__first_name", "user__last_name")
        ]

    initial_payload = {
        "classId": selected_class.id if selected_class else None,
        "date": selected_date.isoformat(),
        "snapshot": snapshot,
        "summary": status_summary,
        "class": {
            "id": selected_class.id,
            "label": f"Class {selected_class.grade}-{selected_class.section}",
            "academic_year": str(selected_class.academic_year),
        } if selected_class else None,
    }

    context = {
        "classes": classes,
        "selected_class": selected_class,
        "selected_date": selected_date,
        "status_summary": status_summary,
        "student_roster": student_roster,
        "initial_payload": initial_payload,
    }
    return render(request, "teacher/view_attendance.html", context)


@login_required
def student_dashboard(request: HttpRequest) -> HttpResponse:
    if getattr(request.user, "role", None) != "student":
        return HttpResponseForbidden("Students only")

    try:
        student = Student.objects.select_related("school_class").get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Contact your administrator.")
        return redirect("logout_get")

    records_qs = (
        AttendanceRecord.objects.filter(student=student)
        .select_related("school_class", "academic_year")
        .order_by("-date", "-created_at")
    )
    records = list(records_qs)

    status_counts: dict[str, int] = {"present": 0, "absent": 0, "late": 0, "excused": 0}
    history_entries: list[dict] = []
    for record in records:
        status_counts[record.status] = status_counts.get(record.status, 0) + 1
        history_entries.append(
            {
                "date": record.date,
                "status": record.status,
                "class_label": str(record.school_class) if record.school_class else "-",
                "academic_year": str(record.academic_year) if record.academic_year else "-",
                "confidence": record.confidence,
                "confidence_percent": round(record.confidence * 100, 1) if record.confidence else None,
            }
        )

    total_marked = len(records)
    present_count = status_counts.get("present", 0)
    attendance_percentage = round((present_count / total_marked) * 100, 1) if total_marked else 0.0

    context = {
        "student": student,
        "status_counts": status_counts,
        "total_marked": total_marked,
        "attendance_percentage": attendance_percentage,
        "history": history_entries,
    }
    return render(request, "student/dashboard.html", context)


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
def attendance_summary_api(request: HttpRequest) -> JsonResponse:
    if getattr(request.user, "role", None) not in {"teacher", "admin"}:
        return JsonResponse({"error": "Forbidden"}, status=403)

    class_id = request.GET.get("class_id")
    date_param = request.GET.get("date")

    if not class_id or not date_param:
        return JsonResponse({"error": "class_id and date are required"}, status=400)

    try:
        class_id_int = int(class_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid class_id"}, status=400)

    try:
        target_date = date.fromisoformat(date_param)
    except ValueError:
        return JsonResponse({"error": "Invalid date"}, status=400)

    school_class = get_object_or_404(SchoolClass, id=class_id_int)
    if not _user_can_access_class(request.user, school_class):
        return JsonResponse({"error": "Forbidden"}, status=403)

    snapshot = _attendance_snapshot(school_class, target_date)
    summary = _status_breakdown(snapshot)

    response = {
        "date": target_date.isoformat(),
        "class": {
            "id": school_class.id,
            "label": f"Class {school_class.grade}-{school_class.section}",
            "academic_year": str(school_class.academic_year),
        },
        "students": snapshot,
        "summary": summary,
    }
    return JsonResponse(response)


@login_required
def attendance_student_history_api(request: HttpRequest, student_id: int) -> JsonResponse:
    if getattr(request.user, "role", None) not in {"teacher", "admin"}:
        return JsonResponse({"error": "Forbidden"}, status=403)

    student = get_object_or_404(Student.objects.select_related("user", "school_class"), pk=student_id)

    allowed_classes_qs = _classes_for_user(request.user)
    allowed_class_ids = set(allowed_classes_qs.values_list("id", flat=True))

    if getattr(request.user, "role", None) == "teacher" and not allowed_class_ids:
        return JsonResponse({"error": "No classes assigned"}, status=403)

    if allowed_class_ids and student.school_class_id and student.school_class_id not in allowed_class_ids and getattr(request.user, "role", None) == "teacher":
        return JsonResponse({"error": "Forbidden"}, status=403)

    records_qs = AttendanceRecord.objects.filter(student=student)
    if allowed_class_ids:
        records_qs = records_qs.filter(school_class_id__in=allowed_class_ids)

    records = [
        {
            "date": rec.date.isoformat(),
            "status": rec.status,
            "confidence": rec.confidence,
            "class": f"Class {rec.school_class.grade}-{rec.school_class.section}",
            "academic_year": str(rec.academic_year),
        }
        for rec in records_qs.select_related("school_class", "academic_year").order_by("-date", "school_class__grade", "school_class__section")
    ]

    response = {
        "student": {
            "id": student.pk,
            "name": student.get_full_name(),
            "roll_number": student.roll_number,
        },
        "records": records,
    }
    return JsonResponse(response)


@login_required
@require_POST
def recognize_frame(request: HttpRequest) -> JsonResponse:
    """
    Receives a video frame, runs face recognition, and returns results.
    This view also handles marking attendance in the database.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    # If face recognition libs aren't available, return a graceful empty result
    if (face_recognition is None) or (np is None):
        return JsonResponse({
            "faces_detected": 0,
            "matched": [],
            "detections": [],
            "used_face_recognition": False,
        })

    try:
        data = json.loads(request.body)
        image_data = base64.b64decode(data["image"].split(",")[1])
        class_id = data.get("class_id")
    except (json.JSONDecodeError, KeyError, IndexError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not class_id:
        return JsonResponse({"error": "class_id is required"}, status=400)

    school_class = get_object_or_404(SchoolClass, id=class_id)
    if not _user_can_access_class(request.user, school_class):
        return JsonResponse({"error": "Forbidden"}, status=403)

    # Decode the image using Pillow to avoid relying on cv2.imdecode
    try:
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        frame_rgb = np.array(image)
    except Exception:
        return JsonResponse({"error": "Invalid image data"}, status=400)

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
    student = get_object_or_404(Student.objects.select_related("school_class"), pk=student_id)
    school_class = student.school_class
    if school_class is None:
        return JsonResponse({"ok": False, "error": "Student not in a class"}, status=400)
    if not _user_can_access_class(request.user, school_class):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    today = timezone.localdate()
    academic_year = school_class.academic_year
    if academic_year is None:
        return JsonResponse({"ok": False, "error": "Academic year missing"}, status=400)
    teacher = None
    daily_excused_count = 0
    if getattr(request.user, "role", None) == "teacher":
        teacher = Teacher.objects.filter(user=request.user).select_related("user").first()
        if teacher is None:
            return JsonResponse({"ok": False, "error": "Teacher profile missing"}, status=400)
        daily_excused_count = ManualExcuseLog.objects.filter(teacher=teacher, date=today).count()

    record = AttendanceRecord.objects.filter(
        student=student,
        school_class=school_class,
        date=today,
        academic_year=academic_year,
    ).first()

    previous_status: str | None = record.status if record else None
    status_changed = False

    def limit_reached() -> bool:
        return teacher is not None and daily_excused_count >= 5

    if record is None:
        if limit_reached():
            return JsonResponse({"ok": False, "error": "Excused limit reached (5 per day)."}, status=400)
        record = AttendanceRecord.objects.create(
            student=student,
            school_class=school_class,
            date=today,
            academic_year=academic_year,
            status="excused",
            confidence=1.0,
        )
        status_changed = True
    elif record.status != "excused":
        if limit_reached():
            return JsonResponse({"ok": False, "error": "Excused limit reached (5 per day)."}, status=400)
        previous_status = record.status
        record.status = "excused"
        record.confidence = 1.0
        record.save(update_fields=["status", "confidence"])
        status_changed = True

    if teacher is not None and status_changed:
        ManualExcuseLog.objects.create(
            teacher=teacher,
            student=student,
            school_class=school_class,
            date=today,
        )
        daily_excused_count += 1

    limit_remaining = max(0, 5 - daily_excused_count) if teacher is not None else None

    return JsonResponse({
        "ok": True,
        "status": record.status,
        "previous_status": previous_status,
        "limit_remaining": limit_remaining,
    })


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