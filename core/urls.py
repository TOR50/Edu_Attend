from django.urls import path
from . import views

urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/students/', views.admin_students, name='admin_students'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/attendance/', views.attendance_overview, name='attendance_overview'),
    path('teacher/attendance/live/', views.take_attendance_entry, name='take_attendance_entry'),
    path('teacher/class/<int:class_id>/take/', views.take_attendance, name='take_attendance'),
    path('api/recognize/', views.recognize_frame, name='recognize_frame'),
    path('api/diagnostics/', views.class_diagnostics, name='class_diagnostics'),
    path('api/attendance/summary/', views.attendance_summary_api, name='attendance_summary_api'),
    path('api/attendance/student/<int:student_id>/history/', views.attendance_student_history_api, name='attendance_student_history_api'),
    path('api/mark-present/<int:student_id>/', views.mark_present, name='mark_present'),
    path('admin/student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('admin/sample/<int:sample_id>/delete/', views.delete_face_sample, name='delete_face_sample'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
]
