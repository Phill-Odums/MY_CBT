from django.contrib import admin
from .models import Subject, Question, ExamConfig, StudentExam, StudentAnswer


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'question_count']
    search_fields = ['name']
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'subject', 'difficulty', 'correct_answer', 'is_active', 'created_at']
    list_filter = ['subject', 'difficulty', 'is_active', 'created_at']
    search_fields = ['text', 'subject__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('subject', 'text', 'difficulty', 'is_active')
        }),
        ('Answer Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
        ('Additional Info', {
            'fields': ('explanation', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    text_preview.short_description = 'Question'


@admin.register(ExamConfig)
class ExamConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_questions', 'time_limit_minutes', 'pass_percentage', 'is_active']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['questions']
    
    fieldsets = (
        ('Exam Configuration', {
            'fields': ('name', 'is_active')
        }),
        ('Exam Settings', {
            'fields': ('total_questions', 'time_limit_minutes', 'pass_percentage')
        }),
        ('Questions', {
            'fields': ('questions',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Filter to only show active questions
        form.base_fields['questions'].queryset = Question.objects.filter(is_active=True)
        return form


@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'student_id', 'exam_config', 'score_display', 'status', 'start_time']
    list_filter = ['status', 'exam_config', 'start_time', 'passed']
    search_fields = ['student_name', 'student_id']
    readonly_fields = ['start_time', 'end_time', 'score', 'passed']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student_name', 'student_id')
        }),
        ('Exam Details', {
            'fields': ('exam_config', 'total_questions', 'status')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Results', {
            'fields': ('score', 'passed')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Exams are created through the web interface
    
    def score_display(self, obj):
        if obj.score is not None:
            percentage = obj.get_score_percentage()
            return f"{obj.score}/{obj.total_questions} ({percentage}%)"
        return "Not graded"
    score_display.short_description = 'Score'


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['exam', 'question_preview', 'selected_answer', 'correct_answer', 'is_correct']
    list_filter = ['is_correct', 'exam__exam_config']
    search_fields = ['exam__student_name', 'question__text']
    readonly_fields = ['exam', 'question', 'selected_answer', 'is_correct', 'answered_at']
    
    def has_add_permission(self, request):
        return False  # Answers are created during exams
    
    def question_preview(self, obj):
        return obj.question.text[:80] + '...' if len(obj.question.text) > 80 else obj.question.text
    question_preview.short_description = 'Question'
    
    def correct_answer(self, obj):
        return obj.question.correct_answer
    correct_answer.short_description = 'Correct Answer'


# Admin site customization
admin.site.site_header = "CBT Examination System Administration"
admin.site.site_title = "CBT Admin"
admin.site.index_title = "Welcome to CBT Administration Panel"
