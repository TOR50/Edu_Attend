from __future__ import annotations
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')

class AcademicYear(models.Model):
    """Represents a school year, e.g., '2024-2025'."""
    year = models.CharField(max_length=9, unique=True, help_text="Format: YYYY-YYYY")
    is_active = models.BooleanField(default=True, help_text="Is this the current academic year?")

    def __str__(self) -> str:
        return self.year

class SchoolClass(models.Model):
    grade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Class/Grade number (1-12)"
    )
    section = models.CharField(
        max_length=2,
        help_text="Section letter, e.g., A, B, C",
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, default=1)

    def __str__(self) -> str:
        return f"Class {self.grade}-{self.section.upper()} ({self.academic_year})"

    class Meta:
        unique_together = ("academic_year", "grade", "section")

    def save(self, *args, **kwargs):
        # Normalize section to uppercase
        if self.section:
            self.section = self.section.upper()
        super().save(*args, **kwargs)

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classes = models.ManyToManyField(SchoolClass, blank=True)

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    roll_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='students/', blank=True, null=True, help_text="A single, high-quality frontal face shot for the main profile.")
    face_encodings = models.JSONField(default=list, blank=True, help_text="Auto-generated from the main photo if face_recognition is installed.")

    class Meta:
        unique_together = ('school_class', 'roll_number')

    def __str__(self) -> str:
        return self.get_full_name()

    def get_full_name(self) -> str:
        return self.user.get_full_name() or self.user.username

class FaceSample(models.Model):
    """Stores multiple face clippings for a student to improve recognition accuracy."""
    student = models.ForeignKey(Student, related_name='samples', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='face_samples/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Sample for {self.student.get_full_name()} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    confidence = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('student', 'school_class', 'date')

    def __str__(self) -> str:
        return f"{self.student} - {self.school_class} on {self.date}: {self.get_status_display()}"
