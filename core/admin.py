from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import User, SchoolClass, Student, Teacher, AttendanceRecord, AcademicYear

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('year',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role", "is_staff")

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("grade", "section", "academic_year")
    list_filter = ("academic_year", "grade", "section")
    search_fields = ("=grade", "section", "academic_year__year")

class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["user", "school_class", "roll_number", "photo"]

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if not photo:
            return photo
        # Limit to ~5 MB to avoid backend storage issues
        max_bytes = 5 * 1024 * 1024
        if hasattr(photo, 'size') and photo.size and photo.size > max_bytes:
            raise ValidationError("Image too large. Please upload a photo under 5 MB.")
        return photo

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ("get_full_name", "user", "school_class", "roll_number")
    list_filter = ("school_class",)
    search_fields = ("user__first_name", "user__last_name", "user__email", "roll_number")
    # Require selecting an existing User when adding a Student in the admin
    raw_id_fields = ("user",)
    # Show face_encodings but don't allow editing directly
    readonly_fields = ("face_encodings",)
    fields = ("user", "school_class", "roll_number", "photo", "face_encodings")

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user",)

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "school_class", "date", "status", "confidence")
    list_filter = ("date", "status", "school_class")
    search_fields = ("student__user__first_name", "student__user__last_name", "=school_class__grade", "school_class__section")
