from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student, FaceSample

from django.db import transaction

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import re

class CustomSignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_roles = [choice for choice in User.ROLE_CHOICES if choice[0] in {"teacher", "student"}]
        self.fields['role'].choices = allowed_roles
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in {"teacher", "student"}:
            raise forms.ValidationError("Only teacher and student accounts can be created here.")
        return role

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})


class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Student
        fields = ['school_class', 'roll_number', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text_input_class = 'input-control'
        select_class = 'input-control select-control'

        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'First name',
            'class': text_input_class,
            'autocomplete': 'given-name',
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Last name',
            'class': text_input_class,
            'autocomplete': 'family-name',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'name@example.com',
            'class': text_input_class,
            'autocomplete': 'email',
            'inputmode': 'email',
        })
        self.fields['roll_number'].widget.attrs.update({
            'placeholder': 'Roll number',
            'class': text_input_class,
        })
        self.fields['school_class'].widget.attrs.update({'class': select_class})
        self.fields['photo'].widget.attrs.update({'class': 'file-control'})
        self.fields['school_class'].empty_label = 'Select a class…'

    @transaction.atomic
    def save(self, commit=True):
        # Create a user for the student
        first = self.cleaned_data['first_name'].lower()
        last = (self.cleaned_data.get('last_name') or '').lower()
        base_username = re.sub(r'[^a-z0-9]+', '', f"{first}{last}") or first or 'student'
        if not base_username:
            base_username = 'student'
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"
        user = User.objects.create_user(
            username=username,
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data.get('last_name', ''),
            role='student'
        )
        
        # Create the student profile
        student = super().save(commit=False)
        student.user = user
        
        if commit:
            student.save()
            self.save_m2m() # For ManyToMany fields if any

        return student


class FaceSampleForm(forms.ModelForm):
    class Meta:
        model = FaceSample
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
