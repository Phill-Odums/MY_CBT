# CBT Examination System - Django Version

A fully-featured Computer-Based Testing (CBT) system built with Django, featuring:
- Student login and exam management
- Configurable exams with dynamic question loading
- Real-time timer and progress tracking
- Comprehensive admin panel for managing questions and exams
- Automatic answer grading and results display

## Features

✅ **Admin Panel Integration**
- Manage questions directly from Django admin
- Add subjects, questions, and answer options
- Configure exam settings and pass marks
- View student exam records and scores

✅ **Student Features**
- Simple login with name and ID
- Clean, intuitive exam interface
- Real-time countdown timer
- Progress bar showing exam progress
- Previous/Next navigation between questions
- Auto-submit when time expires

✅ **Exam Management**
- Multiple exam configurations
- Random question selection
- Configurable number of questions and time limits
- Pass percentage settings
- Detailed results with explanations

## Installation

### Step 1: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
python manage.py migrate
```

### Step 4: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

### Step 5: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Usage

### Accessing the Admin Panel

1. Go to `http://localhost:8000/admin/`
2. Login with your superuser credentials
3. Create subjects and questions

### Setting Up Questions

1. **Create Subjects:**
   - Click on "Subjects"
   - Click "Add Subject"
   - Enter name and description

2. **Add Questions:**
   - Click on "Questions"
   - Click "Add Question"
   - Fill in the question text, options, and correct answer
   - Select difficulty and subject
   - Add an explanation (optional)

3. **Create Exam Configuration:**
   - Click on "Exam Configurations"
   - Click "Add Exam Configuration"
   - Set the number of questions, time limit, and pass percentage
   - Select which questions to include
   - Mark as active

### Student Taking an Exam

1. Go to `http://localhost:8000/`
2. Enter your name and student ID
3. Click "START EXAM"
4. Answer questions using Previous/Next buttons
5. Review your answers before clicking "Submit Exam"
6. View your results with detailed breakdown

## Project Structure

```
CBT_Django/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── cbt_project/          # Project settings
│   ├── __init__.py
│   ├── settings.py       # Django configuration
│   ├── urls.py          # URL routing
│   ├── wsgi.py
│   └── asgi.py
├── cbt_app/             # Main application
│   ├── migrations/
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── exam.html
│   │   ├── submit_exam.html
│   │   ├── results.html
│   │   └── exam_review.html
│   ├── __init__.py
│   ├── admin.py         # Admin customization
│   ├── apps.py
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── forms.py         # Form definitions
│   └── urls.py          # App URL routing
```

## Database Models

### Subject
- Stores exam subject categories

### Question
- Stores multiple-choice questions
- Fields: text, options (A-D), correct_answer, difficulty, explanation

### ExamConfig
- Configurable exam settings
- Fields: name, total_questions, time_limit_minutes, pass_percentage

### StudentExam
- Records student exam sessions
- Fields: student_name, student_id, status, score, passed

### StudentAnswer
- Stores individual student answers
- Fields: exam, question, selected_answer, is_correct

## Admin Features

### Question Management
- Add/Edit/Delete questions
- Filter by subject, difficulty, and status
- Search questions by text
- Bulk operations for activation/deactivation

### Exam Configuration
- Create multiple exam setups
- Associate questions with exams
- Configure difficulty levels

### Student Exam Records
- View all student exams
- Search by student name/ID
- Filter by status and date
- Readonly access to exam data

## Customization

### Styling
Modify `cbt_app/static/css/style.css` to customize the appearance

### Exam Duration
Change `TIME_LIMIT` in `cbt_app/views.py` or configure via admin panel

### Pass Mark
Set pass percentage in the Exam Configuration admin panel

## Security Notes

⚠️ **For Production:**
1. Change `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS` with your domain
4. Use a production database (PostgreSQL recommended)
5. Set up HTTPS
6. Use environment variables for sensitive data

## Troubleshooting

### Database Issues
```bash
python manage.py migrate --run-syncdb
```

### Clear Sessions
```bash
python manage.py clearsessions
```

### Create Backup
```bash
python manage.py dumpdata > backup.json
```

### Restore Backup
```bash
python manage.py loaddata backup.json
```

## Support

For issues or feature requests, please check the application logs:
- Server logs appear in the terminal running the development server
- Admin panel provides detailed question and exam management

## License

This CBT Examination System is provided as-is for educational purposes.
