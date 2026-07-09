import re

from django import forms
from django.core.exceptions import ValidationError
from .models import StudentAnswer, StudentExam, Question, StaffProfile, StaffCourse, StaffQuestion


def validate_password_strength(value):
    """Ensure a password is strong enough for staff or student account creation."""
    if len(value) < 8 or len(value) > 16:
        raise ValidationError("Password must be 8 to 16 characters long and include at least one uppercase letter, one number, and one symbol.")

    if not re.search(r'[A-Z]', value):
        raise ValidationError("Password must be 8 to 16 characters long and include at least one uppercase letter, one number, and one symbol.")

    if not re.search(r'\d', value):
        raise ValidationError("Password must be 8 to 16 characters long and include at least one uppercase letter, one number, and one symbol.")

    if not re.search(r'[^A-Za-z0-9]', value):
        raise ValidationError("Password must be 8 to 16 characters long and include at least one uppercase letter, one number, and one symbol.")

    return value


class StudentLoginForm(forms.Form):
    """Student login form for entering name and ID."""
    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autofocus': True
        })
    )
    student_id = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your student ID'
        })
    )

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if len(full_name) < 2:
            raise forms.ValidationError("Full name must be at least 2 characters.")
        return full_name

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id', '').strip()
        if len(student_id) < 2:
            raise forms.ValidationError("Student ID must be at least 2 characters.")
        return student_id


class CourseCodeForm(forms.Form):
    """Form for students to enter course registration code."""
    course_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter course registration code',
            'autofocus': True,
            'style': 'text-transform: uppercase;'
        })
    )

    def clean_course_code(self):
        course_code = self.cleaned_data.get('course_code', '').strip().upper()
        if len(course_code) < 2:
            raise forms.ValidationError("Course code must be at least 2 characters.")
        try:
            StaffCourse.objects.get(registration_code=course_code, is_active=True)
        except StaffCourse.DoesNotExist:
            raise forms.ValidationError("Invalid or inactive course code.")
        return course_code


class ExamAnswerForm(forms.ModelForm):
    """Form for submitting a single exam answer."""
    
    class Meta:
        model = StudentAnswer
        fields = ['selected_answer']
        widgets = {
            'selected_answer': forms.RadioSelect(
                choices=Question.ANSWER_CHOICES,
                attrs={'class': 'form-check-input'}
            )
        }


class ExamSubmissionForm(forms.Form):
    """Confirmation form for submitting exam."""
    confirm = forms.BooleanField(
        required=True,
        label="I confirm that I have completed and want to submit my exam.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


# ==========================================
# STAFF FORMS
# ==========================================

class StaffRegistrationForm(forms.ModelForm):
    """Form for staff registration."""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        validators=[validate_password_strength]
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = StaffProfile
        fields = ['institution', 'department', 'phone']
        widgets = {
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Institution/School name'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department (optional)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (optional)'
            }),
        }

    def clean_username(self):
        from django.contrib.auth.models import User
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        from django.contrib.auth.models import User
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        return validate_password_strength(password)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class StaffCourseForm(forms.ModelForm):
    """Form for staff to create a course."""
    
    class Meta:
        model = StaffCourse
        fields = ['course_name', 'description', 'total_questions', 'time_limit_minutes', 'pass_percentage']
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course/Exam name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Course description (optional)',
                'rows': 3
            }),
            'total_questions': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 300
            }),
            'pass_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
        }


class StaffQuestionForm(forms.ModelForm):
    """Form for staff to create questions."""
    
    class Meta:
        model = StaffQuestion
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'difficulty', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Question text',
                'rows': 3
            }),
            'option_a': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option A'
            }),
            'option_b': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option B'
            }),
            'option_c': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option C'
            }),
            'option_d': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option D'
            }),
            'correct_answer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explanation (optional)',
                'rows': 2
            }),
        }
