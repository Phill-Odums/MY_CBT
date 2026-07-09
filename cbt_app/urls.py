from django.urls import path
from . import views

app_name = 'cbt'

urlpatterns = [
    # ==========================================
    # STUDENT VIEWS - DEFAULT EXAM
    # ==========================================
    # Route names in this file are used by templates and views.
    # Add a new route here whenever a new page is created in cbt_app/templates/.
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('exam/', views.exam_view, name='exam'),
    path('exam/progress/', views.get_exam_progress, name='exam_progress'),
    path('exam/save-answer/', views.save_exam_answer_view, name='save_exam_answer'),
    path('submit/', views.submit_exam_view, name='submit_exam'),
    path('results/<int:exam_id>/', views.results_view, name='results'),
    path('review/<int:exam_id>/', views.exam_review_view, name='exam_review'),
    
    # ==========================================
    # STAFF VIEWS
    # ==========================================
    path('staff/register/', views.staff_register_view, name='staff_register'),
    path('staff/login/', views.staff_login_view, name='staff_login'),
    path('staff/logout/', views.staff_logout_view, name='staff_logout'),
    path('staff/dashboard/', views.staff_dashboard_view, name='staff_dashboard'),
    path('staff/course/create/', views.staff_create_course_view, name='staff_create_course'),
    path('staff/course/<int:course_id>/', views.staff_course_detail_view, name='staff_course_detail'),
    path('staff/course/<int:course_id>/question/add/', views.staff_add_question_view, name='staff_add_question'),
    path('staff/course/<int:course_id>/question/<int:question_id>/edit/', views.staff_edit_question_view, name='staff_edit_question'),
    path('staff/course/<int:course_id>/question/<int:question_id>/delete/', views.staff_delete_question_view, name='staff_delete_question'),
    path('staff/course/<int:course_id>/results/', views.staff_course_results_view, name='staff_course_results'),
    path('staff/course/<int:course_id>/exam/<int:exam_id>/', views.staff_student_exam_detail_view, name='staff_student_exam_detail'),
    
    # ==========================================
    # STUDENT VIEWS - STAFF COURSES
    # ==========================================
    path('course/code/', views.student_course_code_view, name='student_course_code'),
    path('course/login/', views.student_staff_course_login_view, name='student_staff_course_login'),
    path('course/exam/', views.student_staff_exam_view, name='student_staff_exam'),
    path('course/exam/save-answer/', views.save_staff_exam_answer_view, name='save_staff_exam_answer'),
    path('course/submit/', views.student_staff_submit_exam_view, name='student_staff_submit_exam'),
    path('course/results/<int:exam_id>/', views.student_staff_results_view, name='student_staff_results'),
]
