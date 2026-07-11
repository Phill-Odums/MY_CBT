from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import timedelta
import json
import random

from .models import (
    Question, StudentExam, StudentAnswer, ExamConfig, Subject,
    StaffProfile, StaffCourse, StaffQuestion, StaffStudentExam, StaffStudentAnswer
)
from .forms import (
    StudentLoginForm, ExamAnswerForm, ExamSubmissionForm, CourseCodeForm,
    StaffRegistrationForm, StaffCourseForm, StaffQuestionForm
)

# Frontend rendering map
# Each view below renders a specific HTML template and is linked through cbt_app/urls.py.
# Template location: cbt_app/templates/
# - login_view -> login.html (route: /login/)
# - exam_view -> exam.html (route: /exam/)
# - submit_exam_view -> submit_exam.html (route: /submit/)
# - results_view -> results.html (route: /results/<exam_id>/)
# - staff_login_view -> staff_login.html (route: /staff/login/)
# - staff_dashboard_view -> staff_dashboard.html (route: /staff/dashboard/)
# - staff_course_detail_view -> staff_course_detail.html (route: /staff/course/<course_id>/)
# - student_course_code_view -> student_course_code.html (route: /course/code/)
# - student_staff_exam_view -> student_staff_exam.html (route: /course/exam/)
#
# To add a new frontend page:
# 1. Create the HTML file in cbt_app/templates/.
# 2. Add a view function here that renders that template.
# 3. Register the URL in cbt_app/urls.py.
# 4. Link to it from another template with {% url 'cbt:route_name' %}.
# 5. Use reverse('cbt:route_name') inside Python views when redirecting.


def build_question_payload(question_objects, saved_answers=None):
    """Build a JSON-friendly payload for client-side exam rendering."""
    saved_answers = saved_answers or {}
    payload = []

    for question in question_objects:
        option_pairs = []
        if hasattr(question, 'get_all_options'):
            option_pairs = question.get_all_options()
        else:
            option_pairs = [
                ('A', getattr(question, 'option_a', '')),
                ('B', getattr(question, 'option_b', '')),
                ('C', getattr(question, 'option_c', '')),
                ('D', getattr(question, 'option_d', '')),
            ]

        payload.append({
            'id': question.id,
            'text': question.text,
            'selected_answer': saved_answers.get(question.id),
            'options': [
                {'value': option_letter, 'text': option_text}
                for option_letter, option_text in option_pairs
            ],
        })

    return payload


# ==========================================
# LOGIN & SESSION MANAGEMENT
# ==========================================

def index(request):
    """Home page - redirects to login if no active exam."""
    if 'exam_id' in request.session:
        return redirect('cbt:exam')
    return redirect('cbt:login')


def login_view(request):
    """Student login screen - collect name and ID."""
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name'].strip()
            student_id = form.cleaned_data['student_id'].strip()

            # Get the active exam config
            exam_config = ExamConfig.objects.filter(is_active=True).first()
            if not exam_config:
                return render(request, 'login.html', {
                    'form': form,
                    'error': 'No active exam available. Please contact administrator.'
                })

            # Check if student has already completed this exam
            existing_exam = StudentExam.objects.filter(
                student_id=student_id,
                exam_config=exam_config,
                status__in=['submitted', 'graded']
            ).first()

            if existing_exam:
                # Student has already taken this exam
                error_message = f"You have already completed this exam. Your score: {existing_exam.score}/{existing_exam.total_questions} ({existing_exam.get_score_percentage()}%)"
                return render(request, 'login.html', {
                    'form': form,
                    'exam_config': exam_config,
                    'error': error_message,
                    'already_taken': True,
                    'previous_exam_id': existing_exam.id
                })

            # Create exam session
            exam = StudentExam.objects.create(
                student_name=full_name,
                student_id=student_id,
                exam_config=exam_config,
                total_questions=exam_config.total_questions
            )

            # Store exam info in session
            request.session['exam_id'] = exam.id
            request.session['student_name'] = full_name
            request.session['student_id'] = student_id
            request.session['exam_start_time'] = exam.start_time.isoformat()
            request.session['time_limit_minutes'] = exam_config.time_limit_minutes

            # Get questions for this exam
            questions = exam_config.questions.filter(is_active=True)
            if not questions.exists():
                return render(request, 'login.html', {
                    'form': form,
                    'error': 'No questions available for this exam.'
                })

            # Select random subset
            available_questions = list(questions)
            selected_questions = random.sample(
                available_questions,
                min(exam_config.total_questions, len(available_questions))
            )

            # Store selected question IDs for later grading and replay
            request.session['question_ids'] = [q.id for q in selected_questions]
            request.session['current_question_index'] = 0

            exam.total_questions = len(selected_questions)
            exam.save(update_fields=['total_questions'])

            return redirect('cbt:exam')
    else:
        form = StudentLoginForm()

    exam_config = ExamConfig.objects.filter(is_active=True).first()
    context = {
        'form': form,
        'exam_config': exam_config,
    }
    return render(request, 'login.html', context)


def logout_view(request):
    """Clear exam session."""
    request.session.flush()
    return redirect('cbt:login')


# ==========================================
# EXAM SCREEN
# ==========================================

def exam_view(request):
    """Main exam screen - display questions and handle answers."""
    
    # Verify session
    if 'exam_id' not in request.session:
        return redirect('login')

    exam_id = request.session.get('exam_id')
    exam = get_object_or_404(StudentExam, id=exam_id)

    # Check if exam time has expired
    if exam.status == 'in_progress':
        start_time = timezone.datetime.fromisoformat(request.session['exam_start_time'])
        time_limit = timedelta(minutes=request.session['time_limit_minutes'])
        elapsed = timezone.now() - start_time

        if elapsed > time_limit:
            # Auto-submit exam
            return redirect('cbt:submit_exam')

    question_ids = request.session.get('question_ids', [])
    if not question_ids:
        return redirect('cbt:submit_exam')

    questions = list(Question.objects.filter(id__in=question_ids, is_active=True))
    ordered_questions = {question.id: question for question in questions}
    questions = [ordered_questions[question_id] for question_id in question_ids if question_id in ordered_questions]

    if not questions:
        return redirect('cbt:submit_exam')

    saved_answers = dict(
        StudentAnswer.objects.filter(exam=exam, question__in=questions).values_list('question_id', 'selected_answer')
    )
    question_payload = build_question_payload(questions, saved_answers)

    start_time = timezone.datetime.fromisoformat(request.session['exam_start_time'])
    time_limit = timedelta(minutes=request.session['time_limit_minutes'])
    elapsed = timezone.now() - start_time
    time_remaining = time_limit - elapsed

    minutes = max(0, int(time_remaining.total_seconds()) // 60)
    seconds = max(0, int(time_remaining.total_seconds()) % 60)
    time_warning = time_remaining.total_seconds() < 300

    context = {
        'exam': exam,
        'question_payload': json.dumps(question_payload),
        'total_questions': len(question_ids),
        'progress_percentage': 0,
        'time_remaining': f"{minutes:02d}:{seconds:02d}",
        'time_warning': time_warning,
        'save_answer_url': reverse('cbt:save_exam_answer'),
        'submit_url': reverse('cbt:submit_exam'),
        'exam_id': exam.id,
    }

    return render(request, 'exam.html', context)  


@csrf_exempt
@require_GET
def get_exam_progress(request):
    """AJAX endpoint to get exam progress and time remaining."""
    if 'exam_id' in request.session:
        exam_id = request.session.get('exam_id')
        exam = get_object_or_404(StudentExam, id=exam_id)
        question_ids = request.session.get('question_ids', [])
        start_time = timezone.datetime.fromisoformat(request.session['exam_start_time'])
        time_limit = timedelta(minutes=request.session['time_limit_minutes'])
    elif 'staff_exam_id' in request.session:
        exam_id = request.session.get('staff_exam_id')
        exam = get_object_or_404(StaffStudentExam, id=exam_id)
        question_ids = request.session.get('staff_question_ids', [])
        start_time = timezone.datetime.fromisoformat(request.session['staff_exam_start_time'])
        time_limit = timedelta(minutes=exam.course.time_limit_minutes)
    else:
        return JsonResponse({
            'time_expired': True,
            'time_remaining': '00:00'
        })

    elapsed = timezone.now() - start_time
    time_remaining = time_limit - elapsed

    total_seconds = max(0, int(time_remaining.total_seconds()))
    if total_seconds <= 0:
        return JsonResponse({
            'time_expired': True,
            'time_remaining': '00:00'
        })

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return JsonResponse({
        'time_expired': False,
        'time_remaining': f"{minutes:02d}:{seconds:02d}",
        'current_question': 1,
        'total_questions': len(question_ids),
        'progress': 0 if not question_ids else 0
    })


@require_POST
def save_exam_answer_view(request):
    """Persist a student's selected answer to the server."""
    if 'exam_id' not in request.session:
        return JsonResponse({'error': 'No active exam'}, status=400)

    exam_id = request.session.get('exam_id')
    exam = get_object_or_404(StudentExam, id=exam_id)

    question_id = request.POST.get('question_id')
    selected_answer = request.POST.get('selected_answer')

    if not question_id or selected_answer not in dict(Question.ANSWER_CHOICES):
        return JsonResponse({'error': 'Invalid answer payload'}, status=400)

    question = get_object_or_404(Question, id=question_id)
    answer, _ = StudentAnswer.objects.get_or_create(exam=exam, question=question)
    answer.selected_answer = selected_answer
    answer.save(update_fields=['selected_answer'])

    return JsonResponse({'status': 'saved'})


@require_POST
def save_staff_exam_answer_view(request):
    """Persist a student's staff-course selected answer to the server."""
    if 'staff_exam_id' not in request.session:
        return JsonResponse({'error': 'No active exam'}, status=400)

    exam_id = request.session.get('staff_exam_id')
    exam = get_object_or_404(StaffStudentExam, id=exam_id)

    question_id = request.POST.get('question_id')
    selected_answer = request.POST.get('selected_answer')

    if not question_id or selected_answer not in dict(StaffQuestion.ANSWER_CHOICES):
        return JsonResponse({'error': 'Invalid answer payload'}, status=400)

    question = get_object_or_404(StaffQuestion, id=question_id)
    answer, _ = StaffStudentAnswer.objects.get_or_create(exam=exam, question=question)
    answer.selected_answer = selected_answer
    answer.save(update_fields=['selected_answer'])

    return JsonResponse({'status': 'saved'})


# ==========================================
# EXAM SUBMISSION & RESULTS
# ==========================================

def submit_exam_view(request):
    """Submit exam and grade it."""
    
    if 'exam_id' not in request.session:
        return redirect('login')

    exam_id = request.session.get('exam_id')
    exam = get_object_or_404(StudentExam, id=exam_id)

    if exam.status != 'in_progress':
        return redirect('cbt:results', exam_id=exam_id)

    if request.method == 'POST':
        form = ExamSubmissionForm(request.POST)
        if form.is_valid():
            question_ids = request.session.get('question_ids', [])
            answers_payload = request.POST.get('answers_payload', '{}')

            try:
                submitted_answers = json.loads(answers_payload)
            except (TypeError, ValueError):
                submitted_answers = {}

            correct_count = 0

            for question_id in question_ids:
                selected_answer = submitted_answers.get(str(question_id))
                if selected_answer is None:
                    existing_answer = StudentAnswer.objects.filter(exam=exam, question_id=question_id).first()
                    if existing_answer:
                        selected_answer = existing_answer.selected_answer
                    else:
                        selected_answer = None

                if selected_answer is not None:
                    answer, _ = StudentAnswer.objects.get_or_create(exam=exam, question_id=question_id)
                    answer.selected_answer = selected_answer
                    answer.check_answer()
                    answer.save()
                    if answer.is_correct:
                        correct_count += 1

            exam.score = correct_count
            exam.end_time = timezone.now()
            exam.status = 'graded'

            pass_percentage = exam.exam_config.pass_percentage
            score_percentage = (correct_count / exam.total_questions) * 100 if exam.total_questions else 0
            exam.passed = score_percentage >= pass_percentage

            exam.save()

            request.session.flush()

            return redirect('cbt:results', exam_id=exam_id)
    else:
        form = ExamSubmissionForm()

    context = {
        'exam': exam,
        'form': form,
    }
    return render(request, 'submit_exam.html', context)


def results_view(request, exam_id):
    """Display exam results."""
    
    exam = get_object_or_404(StudentExam, id=exam_id)

    if exam.status != 'graded':
        return redirect('cbt:login')

    # Get all answers with question details
    answers = StudentAnswer.objects.filter(exam=exam).select_related('question').order_by('question__id')

    score_percentage = exam.get_score_percentage()
    time_taken = exam.get_time_taken()

    # Format time taken
    if time_taken:
        minutes = time_taken // 60
        seconds = time_taken % 60
        time_display = f"{minutes}m {seconds}s"
    else:
        time_display = "N/A"

    context = {
        'exam': exam,
        'answers': answers,
        'score_percentage': score_percentage,
        'time_display': time_display,
        'pass_mark': exam.exam_config.pass_percentage,
    }
    return render(request, 'results.html', context)


# ==========================================
# REVIEW & ADMIN HELPERS
# ==========================================

def exam_review_view(request, exam_id):
    """Review exam answers (detailed breakdown)."""
    
    exam = get_object_or_404(StudentExam, id=exam_id)

    if exam.status != 'graded':
        return redirect('cbt:login')

    answers = StudentAnswer.objects.filter(exam=exam).select_related('question').order_by('question__id')

    context = {
        'exam': exam,
        'answers': answers,
    }
    return render(request, 'exam_review.html', context)


# ==========================================
# STAFF VIEWS
# ==========================================

def staff_register_view(request):
    """Staff registration page."""
    if request.user.is_authenticated and hasattr(request.user, 'staff_profile'):
        return redirect('cbt:staff_dashboard')

    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password']
            )

            # Create staff profile
            staff_profile = StaffProfile.objects.create(
                user=user,
                institution=form.cleaned_data.get('institution', ''),
                department=form.cleaned_data.get('department', ''),
                phone=form.cleaned_data.get('phone', '')
            )

            # Log user in
            login(request, user)
            return redirect('cbt:staff_dashboard')
    else:
        form = StaffRegistrationForm()

    return render(request, 'staff_register.html', {'form': form})


def staff_login_view(request):
    """Staff login page."""
    if request.user.is_authenticated and hasattr(request.user, 'staff_profile'):
        return redirect('cbt:staff_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'staff_profile'):
            login(request, user)
            return redirect('cbt:staff_dashboard')
        else:
            return render(request, 'staff_login.html', {'error': 'Invalid credentials or not a staff member.'})
    
    return render(request, 'staff_login.html')


@login_required(login_url='cbt:staff_login')
def staff_dashboard_view(request):
    """Staff dashboard showing courses and statistics."""
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    courses = staff_profile.courses.all().order_by('-created_at')

    context = {
        'staff_profile': staff_profile,
        'courses': courses,
    }
    return render(request, 'staff_dashboard.html', context)


@login_required(login_url='cbt:staff_login')
def staff_create_course_view(request):
    """Create a new course."""
    staff_profile = get_object_or_404(StaffProfile, user=request.user)

    if request.method == 'POST':
        form = StaffCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.staff = staff_profile
            course.save()
            return redirect('cbt:staff_course_detail', course_id=course.id)
    else:
        form = StaffCourseForm()

    return render(request, 'staff_create_course.html', {'form': form})


@login_required(login_url='cbt:staff_login')
def staff_course_detail_view(request, course_id):
    """View course details and manage questions."""
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    course = get_object_or_404(StaffCourse, id=course_id, staff=staff_profile)
    questions = course.questions.all().order_by('-created_at')

    context = {
        'course': course,
        'questions': questions,
        'question_count': questions.count(),
    }
    return render(request, 'staff_course_detail.html', context)


@login_required(login_url='cbt:staff_login')
def staff_add_question_view(request, course_id):
    """Add a question to a course."""
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    course = get_object_or_404(StaffCourse, id=course_id, staff=staff_profile)

    if request.method == 'POST':
        form = StaffQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.course = course
            question.save()
            return redirect('cbt:staff_course_detail', course_id=course.id)
    else:
        form = StaffQuestionForm()

    return render(request, 'staff_add_question.html', {'form': form, 'course': course})


@login_required(login_url='cbt:staff_login')
def staff_edit_question_view(request, course_id, question_id):
    """Edit a question."""
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    course = get_object_or_404(StaffCourse, id=course_id, staff=staff_profile)
    question = get_object_or_404(StaffQuestion, id=question_id, course=course)

    if request.method == 'POST':
        form = StaffQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('cbt:staff_course_detail', course_id=course.id)
    else:
        form = StaffQuestionForm(instance=question)

    return render(request, 'staff_edit_question.html', {'form': form, 'course': course, 'question': question})


@login_required(login_url='cbt:staff_login')
def staff_delete_question_view(request, course_id, question_id):
    """Delete a question."""
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    course = get_object_or_404(StaffCourse, id=course_id, staff=staff_profile)
    question = get_object_or_404(StaffQuestion, id=question_id, course=course)

    if request.method == 'POST':
        question.delete()
        return redirect('cbt:staff_course_detail', course_id=course.id)

    return render(request, 'staff_delete_question.html', {'question': question, 'course': course})


@login_required(login_url='cbt:staff_login')
def staff_course_results_view(request, course_id):
    """View all student results for a course."""
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    course = get_object_or_404(StaffCourse, id=course_id, staff=staff_profile)
    exams = course.student_exams.all().order_by('-start_time')

    context = {
        'course': course,
        'exams': exams,
    }
    return render(request, 'staff_course_results.html', context)


@login_required(login_url='cbt:staff_login')
def staff_student_exam_detail_view(request, course_id, exam_id):
    """View detailed results of a student's exam."""
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    course = get_object_or_404(StaffCourse, id=course_id, staff=staff_profile)
    exam = get_object_or_404(StaffStudentExam, id=exam_id, course=course)
    answers = exam.answers.all().select_related('question').order_by('question__id')

    context = {
        'course': course,
        'exam': exam,
        'answers': answers,
    }
    return render(request, 'staff_student_exam_detail.html', context)


def staff_logout_view(request):
    """Staff logout."""
    logout(request)
    return redirect('cbt:staff_login')


# ==========================================
# STUDENT - STAFF COURSE VIEWS
# ==========================================

def student_course_code_view(request):
    """Student enters course code to access staff-created test."""
    if request.method == 'POST':
        form = CourseCodeForm(request.POST)
        if form.is_valid():
            course_code = form.cleaned_data['course_code'].upper()
            course = get_object_or_404(StaffCourse, registration_code=course_code, is_active=True)
            request.session['course_code'] = course_code
            request.session['course_id'] = course.id
            return redirect('cbt:student_staff_course_login')
    else:
        form = CourseCodeForm()

    return render(request, 'student_course_code.html', {'form': form})


def student_staff_course_login_view(request):
    """Student login for staff course."""
    if 'course_id' not in request.session:
        return redirect('cbt:student_course_code')

    course = get_object_or_404(StaffCourse, id=request.session['course_id'])

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name'].strip()
            student_id = form.cleaned_data['student_id'].strip()

            # Check if student has already completed this exam
            existing_exam = StaffStudentExam.objects.filter(
                course=course,
                student_id=student_id,
                status__in=['submitted', 'graded']
            ).first()

            if existing_exam:
                # Student has already taken this exam
                error_message = f"You have already completed this exam. Your score: {existing_exam.score}/{existing_exam.total_questions} ({existing_exam.get_score_percentage()}%)"
                return render(request, 'student_staff_course_login.html', {
                    'form': form,
                    'course': course,
                    'error': error_message,
                    'already_taken': True,
                    'previous_exam_id': existing_exam.id
                })

            # Create exam session for staff course
            exam = StaffStudentExam.objects.create(
                course=course,
                student_name=full_name,
                student_id=student_id,
                total_questions=course.total_questions
            )

            # Store exam info in session
            request.session['staff_exam_id'] = exam.id
            request.session['student_name'] = full_name
            request.session['student_id'] = student_id
            request.session['staff_exam_start_time'] = exam.start_time.isoformat()

            # Get questions for this course
            questions = course.questions.filter(is_active=True)
            if not questions.exists():
                return render(request, 'student_staff_course_login.html', {
                    'form': form,
                    'course': course,
                    'error': 'No questions available for this course.'
                })

            # Select random subset
            available_questions = list(questions)
            selected_questions = random.sample(
                available_questions,
                min(course.total_questions, len(available_questions))
            )

            # Store question IDs in session
            request.session['staff_question_ids'] = [q.id for q in selected_questions]
            request.session['staff_current_question_index'] = 0

            return redirect('cbt:student_staff_exam')
    else:
        form = StudentLoginForm()

    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'student_staff_course_login.html', context) 


def student_staff_exam_view(request):
    """Student exam screen for staff course."""
    if 'staff_exam_id' not in request.session:
        return redirect('cbt:student_course_code')

    exam_id = request.session.get('staff_exam_id')
    exam = get_object_or_404(StaffStudentExam, id=exam_id)

    if exam.status == 'in_progress':
        start_time = timezone.datetime.fromisoformat(request.session['staff_exam_start_time'])
        time_limit = timedelta(minutes=exam.course.time_limit_minutes)
        elapsed = timezone.now() - start_time

        if elapsed > time_limit:
            return redirect('cbt:student_staff_submit_exam')

    question_ids = request.session.get('staff_question_ids', [])
    if not question_ids:
        return redirect('cbt:student_staff_submit_exam')

    questions = list(StaffQuestion.objects.filter(id__in=question_ids, is_active=True))
    ordered_questions = {question.id: question for question in questions}
    questions = [ordered_questions[question_id] for question_id in question_ids if question_id in ordered_questions]

    if not questions:
        return redirect('cbt:student_staff_submit_exam')

    saved_answers = dict(
        StaffStudentAnswer.objects.filter(exam=exam, question__in=questions).values_list('question_id', 'selected_answer')
    )
    question_payload = build_question_payload(questions, saved_answers)

    start_time = timezone.datetime.fromisoformat(request.session['staff_exam_start_time'])
    time_limit = timedelta(minutes=exam.course.time_limit_minutes)
    elapsed = timezone.now() - start_time
    time_remaining = time_limit - elapsed

    minutes = max(0, int(time_remaining.total_seconds()) // 60)
    seconds = max(0, int(time_remaining.total_seconds()) % 60)
    time_warning = time_remaining.total_seconds() < 300

    context = {
        'exam': exam,
        'question_payload': json.dumps(question_payload),
        'total_questions': len(question_ids),
        'progress_percentage': 0,
        'time_remaining': f"{minutes:02d}:{seconds:02d}",
        'time_warning': time_warning,
        'save_answer_url': reverse('cbt:save_staff_exam_answer'),
        'submit_url': reverse('cbt:student_staff_submit_exam'),
        'exam_id': exam.id,
    }

    return render(request, 'student_staff_exam.html', context)


def student_staff_submit_exam_view(request):
    """Submit staff course exam and grade it."""
    if 'staff_exam_id' not in request.session:
        return redirect('cbt:student_course_code')

    exam_id = request.session.get('staff_exam_id')
    exam = get_object_or_404(StaffStudentExam, id=exam_id)

    if exam.status != 'in_progress':
        return redirect('cbt:student_staff_results', exam_id=exam_id)

    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        if confirm == 'on':
            # Grade the exam
            answers = StaffStudentAnswer.objects.filter(exam=exam)
            correct_count = 0

            for answer in answers:
                answer.is_correct = (answer.selected_answer == answer.question.correct_answer)
                answer.save()
                if answer.is_correct:
                    correct_count += 1

            exam.score = correct_count
            exam.end_time = timezone.now()
            exam.status = 'graded'

            # Determine if passed
            pass_percentage = exam.course.pass_percentage
            score_percentage = (correct_count / exam.total_questions) * 100
            exam.passed = score_percentage >= pass_percentage

            exam.save()

            # Clear session
            request.session.flush()

            return redirect('cbt:student_staff_results', exam_id=exam_id)

    context = {
        'exam': exam,
    }
    return render(request, 'student_staff_submit_exam.html', context)


def student_staff_results_view(request, exam_id):
    """Display staff course exam results."""
    exam = get_object_or_404(StaffStudentExam, id=exam_id)

    if exam.status != 'graded':
        return redirect('cbt:student_course_code')

    answers = StaffStudentAnswer.objects.filter(exam=exam).select_related('question').order_by('question__id')

    score_percentage = exam.get_score_percentage()
    time_taken = exam.get_time_taken()

    if time_taken:
        minutes = time_taken // 60
        seconds = time_taken % 60
        time_display = f"{minutes}m {seconds}s"
    else:
        time_display = "N/A"

    context = {
        'exam': exam,
        'answers': answers,
        'score_percentage': score_percentage,
        'time_display': time_display,
        'pass_mark': exam.course.pass_percentage,
    }
    return render(request, 'student_staff_results.html', context)
