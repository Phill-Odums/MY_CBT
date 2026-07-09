# Frontend Pages and Route Reference

This document explains how the Django frontend pages in this project are rendered, where the HTML files live, and how to connect a new page to the existing app.

## 1. Template Folder
All frontend pages are stored in:
- cbt_app/templates/

## 2. Main Page-to-View Mapping

| View function | Template file | Route | Purpose |
| --- | --- | --- | --- |
| index | N/A | / | Redirects to login or active exam |
| login_view | login.html | /login/ | Student login page |
| exam_view | exam.html | /exam/ | Main exam page |
| submit_exam_view | submit_exam.html | /submit/ | Exam submission confirmation |
| results_view | results.html | /results/<exam_id>/ | Exam results page |
| exam_review_view | exam_review.html | /review/<exam_id>/ | Review submitted answers |

## 3. Staff Page Mapping

| View function | Template file | Route | Purpose |
| --- | --- | --- | --- |
| staff_login_view | staff_login.html | /staff/login/ | Staff login |
| staff_register_view | staff_register.html | /staff/register/ | Staff registration |
| staff_dashboard_view | staff_dashboard.html | /staff/dashboard/ | Staff dashboard |
| staff_create_course_view | staff_create_course.html | /staff/course/create/ | Create course |
| staff_course_detail_view | staff_course_detail.html | /staff/course/<course_id>/ | Course detail |
| staff_add_question_view | staff_add_question.html | /staff/course/<course_id>/question/add/ | Add question |
| staff_edit_question_view | staff_edit_question.html | /staff/course/<course_id>/question/<question_id>/edit/ | Edit question |
| staff_delete_question_view | staff_delete_question.html | /staff/course/<course_id>/question/<question_id>/delete/ | Delete question |
| staff_course_results_view | staff_course_results.html | /staff/course/<course_id>/results/ | Staff results |
| staff_student_exam_detail_view | staff_student_exam_detail.html | /staff/course/<course_id>/exam/<exam_id>/ | Student exam review |

## 4. Student Course / Staff-Course Mapping

| View function | Template file | Route | Purpose |
| --- | --- | --- | --- |
| student_course_code_view | student_course_code.html | /course/code/ | Enter course code |
| student_staff_course_login_view | student_staff_course_login.html | /course/login/ | Student login for staff-created course |
| student_staff_exam_view | student_staff_exam.html | /course/exam/ | Course exam page |
| student_staff_submit_exam_view | student_staff_submit_exam.html | /course/submit/ | Submit course exam |
| student_staff_results_view | student_staff_results.html | /course/results/<exam_id>/ | Course exam result |

## 5. How to Link a New Frontend Page

### Step 1: Create the template
Put the new HTML file in:
- cbt_app/templates/

### Step 2: Add a view in views.py
Example:
```python
from django.shortcuts import render


def new_page_view(request):
    return render(request, 'new_page.html')
```

### Step 3: Register the route in urls.py
Example:
```python
path('new-page/', views.new_page_view, name='new_page'),
```

### Step 4: Link to it from another page
In any template, use:
```django
<a href="{% url 'cbt:new_page' %}">Go to New Page</a>
```

### Step 5: Redirect to it from Python logic
Example:
```python
from django.urls import reverse

return redirect(reverse('cbt:new_page'))
```

## 6. Common Template Inheritance
Most pages extend the base template:
- cbt_app/templates/base.html

So if a new page should share the same layout, extend it like this:
```django
{% extends 'base.html' %}
```

## 7. Notes for Frontend Developers
- Use the existing templates as reference before creating a new page.
- Keep route names stable and descriptive.
- If the page needs data from the backend, pass it through the view context dictionary.
- For forms, use Django templating and the existing form classes in cbt_app/forms.py.

## 8. Where to Look When Building a New Page
- View logic: cbt_app/views.py
- URL mapping: cbt_app/urls.py
- Base layout: cbt_app/templates/base.html
- Existing page examples: cbt_app/templates/
- Form handling: cbt_app/forms.py
