from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import string
import random


class Subject(models.Model):
    """Subject categories for organizing questions."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    """Multiple choice question with 4 options."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    
    ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Activate/Deactivate questions")

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"{self.subject.name}: {self.text[:50]}..."

    def get_correct_text(self):
        """Return the text of the correct answer."""
        option_map = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }
        return option_map.get(self.correct_answer, '')

    def get_all_options(self):
        """Return all options as a list of tuples."""
        return [
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d),
        ]


class ExamConfig(models.Model):
    """Configuration settings for exams."""
    name = models.CharField(max_length=200)
    total_questions = models.IntegerField(
        default=25,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    time_limit_minutes = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1), MaxValueValidator(300)]
    )
    pass_percentage = models.IntegerField(
        default=70,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    questions = models.ManyToManyField(Question, related_name='exams')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Exam Configurations"

    def __str__(self):
        return self.name


class StudentExam(models.Model):
    """Record of a student's exam session."""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]

    student_name = models.CharField(max_length=200)
    student_id = models.CharField(max_length=100)
    exam_config = models.ForeignKey(ExamConfig, on_delete=models.CASCADE)
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )
    
    score = models.IntegerField(null=True, blank=True)
    total_questions = models.IntegerField(default=0)
    passed = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.student_name} ({self.student_id}) - {self.exam_config.name}"

    def get_time_taken(self):
        """Return time taken in seconds, or None if exam not completed."""
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return None

    def get_score_percentage(self):
        """Return score as percentage."""
        if self.score is not None and self.total_questions > 0:
            return int((self.score / self.total_questions) * 100)
        return 0


class StudentAnswer(models.Model):
    """Student's answer to a specific question."""
    exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=Question.ANSWER_CHOICES)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam', 'question')
        ordering = ['question']

    def __str__(self):
        return f"{self.exam} - Q{self.question.id}"

    def check_answer(self):
        """Check if the selected answer is correct."""
        self.is_correct = (self.selected_answer == self.question.correct_answer)
        return self.is_correct


class StaffProfile(models.Model):
    """Staff member profile for creating and managing courses."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    institution = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Staff Profiles"

    def __str__(self):
        return f"Staff: {self.user.get_full_name() or self.user.username}"


class StaffCourse(models.Model):
    """Course created by a staff member with a unique registration code."""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='courses')
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Unique registration code for students
    registration_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True
    )
    
    # Course settings
    total_questions = models.IntegerField(
        default=25,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    time_limit_minutes = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1), MaxValueValidator(300)]
    )
    pass_percentage = models.IntegerField(
        default=70,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course_name} ({self.registration_code})"

    @staticmethod
    def generate_unique_code():
        """Generate a unique 6-character alphanumeric code."""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=6))
            if not StaffCourse.objects.filter(registration_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        """Auto-generate registration code if not provided."""
        if not self.registration_code:
            self.registration_code = self.generate_unique_code()
        super().save(*args, **kwargs)


class StaffQuestion(models.Model):
    """Questions created by staff for their course."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    course = models.ForeignKey(StaffCourse, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Staff Questions"

    def __str__(self):
        return f"{self.course.course_name}: {self.text[:50]}..."

    def get_all_options(self):
        """Return all options as a list of tuples."""
        return [
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d),
        ]


class StaffStudentExam(models.Model):
    """Record of a student's exam session for a staff course."""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]

    course = models.ForeignKey(StaffCourse, on_delete=models.CASCADE, related_name='student_exams')
    student_name = models.CharField(max_length=200)
    student_id = models.CharField(max_length=100)
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )
    
    score = models.IntegerField(null=True, blank=True)
    total_questions = models.IntegerField(default=0)
    passed = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.student_name} ({self.student_id}) - {self.course.course_name}"

    def get_time_taken(self):
        """Return time taken in seconds, or None if exam not completed."""
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return None

    def get_score_percentage(self):
        """Return score as percentage."""
        if self.score is not None and self.total_questions > 0:
            return int((self.score / self.total_questions) * 100)
        return 0


class StaffStudentAnswer(models.Model):
    """Student's answer to a staff question."""
    exam = models.ForeignKey(StaffStudentExam, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(StaffQuestion, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=StaffQuestion.ANSWER_CHOICES)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam', 'question')
        ordering = ['question']

    def __str__(self):
        return f"{self.exam} - Q{self.question.id}"

    def check_answer(self):
        """Check if the selected answer is correct."""
        self.is_correct = (self.selected_answer == self.question.correct_answer)
        return self.is_correct
