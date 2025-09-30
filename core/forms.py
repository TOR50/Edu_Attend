from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student, FaceSample

from django.db import transaction

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomSignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})

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

    @transaction.atomic
    def save(self, commit=True):
        # Create a user for the student
        username = f"{self.cleaned_data['first_name'].lower()}{self.cleaned_data.get('last_name', '').lower()}"
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
