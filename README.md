# CBT Examination System - Django Version

A fully-featured Computer-Based Testing (CBT) system built with Django that enables schools, colleges, training centers, and educational institutions to conduct examinations digitally.

The system has evolved beyond a simple admin-managed CBT platform and now includes a **Multi-Staff Management System**, allowing staff users to independently manage courses, questions, students, and examination records without requiring access to the Django Admin panel.

---

## Key Features

### Student Features

* Secure student login
* Access examinations using assigned course codes
* Clean and intuitive examination interface
* Real-time countdown timer
* Progress tracking and navigation
* Previous/Next question navigation
* Automatic submission when time expires
* Instant grading and score computation
* Detailed result breakdown
* Exam review functionality

### Staff Features (New)

The system now supports multiple staff users who can independently manage examinations.

Staff users can:

* Register and login securely
* Access a dedicated staff dashboard
* Create and manage courses
* Add examination questions
* Edit existing questions
* Delete questions
* View assigned student examination records
* Monitor student performance
* Access examination review reports
* Manage assessments without using Django Admin

### Administrator Features

* Full system administration through Django Admin
* Manage staff and student records
* Configure examination settings
* Monitor system activities
* Manage subjects and global configurations

---

## Multi-Staff Management System

### Why This Update?

Previously, all examination questions, courses, and student records were managed exclusively through Django Admin.

This update introduces a decentralized management structure where multiple staff members can independently manage their own examination content.

### Benefits

* Reduced dependency on Django Admin
* Improved scalability for schools and institutions
* Better separation of responsibilities
* Easier course and examination management
* Enhanced security through role-based access

### Staff Management Capabilities

* Staff Registration
* Staff Login
* Staff Dashboard
* Course Creation
* Question Creation
* Question Editing
* Question Deletion
* Student Exam Monitoring
* Results Management

---

## Features Overview

### Admin Panel Integration

* Manage questions directly from Django Admin
* Add subjects, questions, and answer options
* Configure examination settings
* Set pass marks and time limits
* View student examination records and scores

### Examination Management

* Multiple exam configurations
* Dynamic question loading
* Randomized question selection
* Configurable time limits
* Pass percentage settings
* Detailed result analysis
* Examination review support

### Real-Time Examination Experience

* Countdown timer
* Progress tracking
* Question navigation
* Auto-save capabilities
* Auto-submit functionality

---

## Screens Included in the System

### Student Pages

* Login Page
* Course Code Access Page
* Examination Page
* Submit Examination Page
* Results Page
* Examination Review Page

### Staff Pages

* Staff Registration
* Staff Login
* Staff Dashboard
* Add Course
* Add Question
* Edit Question
* Delete Question
* Student Examination Monitoring
* Student Results Dashboard

---

## Installation

### Step 1: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
python manage.py migrate
```

### Step 4: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 5: Run Development Server

```bash
python manage.py runserver
```

Visit:

```text
http://localhost:8000
```

---

## Usage

### Administrator Setup

1. Login to:

```text
http://localhost:8000/admin/
```

2. Create Subjects

3. Configure Exams

4. Manage Global Settings

### Staff Workflow

1. Register a Staff Account
2. Login to Staff Portal
3. Create Courses
4. Add Examination Questions
5. Manage Existing Questions
6. Monitor Student Activity
7. View Student Results

### Student Workflow

1. Access Homepage
2. Enter Student Information
3. Enter Course Code
4. Take Examination
5. Submit Answers
6. View Results
7. Review Examination

---

## Project Structure

```text
CBT_Django/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── cbt_project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── cbt_app/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── exam.html
│   │   ├── submit_exam.html
│   │   ├── results.html
│   │   ├── exam_review.html
│   │   ├── staff_dashboard.html
│   │   ├── staff_login.html
│   │   ├── staff_register.html
│   │   ├── staff_add_question.html
│   │   ├── staff_edit_question.html
│   │   ├── staff_delete_question.html
│   │   ├── staff_create_course.html
│   │   ├── staff_course_detail.html
│   │   ├── student_staff_exam.html
│   │   ├── student_staff_results.html
│   │   └── staff_student_exam_detail.html
│   │
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
```

---

## Database Models

### Subject

Stores examination subject categories.

### Question

Stores multiple-choice questions.

Fields:

* Question Text
* Option A
* Option B
* Option C
* Option D
* Correct Answer
* Difficulty
* Explanation

### ExamConfig

Stores configurable examination settings.

Fields:

* Name
* Number of Questions
* Time Limit
* Pass Percentage

### StudentExam

Stores examination sessions.

Fields:

* Student Name
* Student ID
* Score
* Status
* Pass/Fail State

### StudentAnswer

Stores individual student responses.

### Staff

Stores staff user information and permissions.

### Course

Stores course information assigned to staff members.

---

## Security Notes

For production deployment:

* Change SECRET_KEY
* Set DEBUG = False
* Configure ALLOWED_HOSTS
* Use PostgreSQL
* Configure HTTPS
* Store secrets in environment variables
* Enable secure session cookies

---

## Troubleshooting

### Database Synchronization

```bash
python manage.py migrate --run-syncdb
```

### Clear Sessions

```bash
python manage.py clearsessions
```

### Backup Database

```bash
python manage.py dumpdata > backup.json
```

### Restore Database

```bash
python manage.py loaddata backup.json
```

---

## Future Improvements

* Excel Question Import
* CSV Question Import
* PDF Result Export
* Email Notifications
* Student Analytics Dashboard
* REST API Integration
* Mobile Responsive Enhancements
* AI-Powered Question Generation
* Online Proctoring Features

---

## Technologies Used

* Python
* Django
* HTML5
* CSS3
* JavaScript
* Bootstrap
* SQLite (Development)
* PostgreSQL (Production Recommended)

---

## Author

**Phillip Odums**

B.Sc. (Ed.) Mathematics / Computer Science

Data Scientist | Machine Learning Engineer | Python Developer

---

## License

This CBT Examination System is provided for educational and learning purposes.
