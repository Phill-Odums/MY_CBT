# Quick Start Guide - CBT Examination System

## 🚀 Getting Started in 5 Minutes

### Step 1: Setup (Windows)
```bash
cd CBT_Django
setup.bat
```

### Step 2: Setup (Linux/Mac)
```bash
cd CBT_Django
chmod +x setup.sh
./setup.sh
```

### Step 3: Load Sample Questions
```bash
python manage.py shell < load_sample_data.py
```

### Step 4: Start the Server
```bash
python manage.py runserver
```

### Step 5: Access the Application
- **Student Exam:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin

---

## 📋 Admin Panel Guide

### Login to Admin
1. Go to http://localhost:8000/admin
2. Use the superuser credentials you created during setup

### Create a Subject
1. Click "Subjects" in the sidebar
2. Click "Add Subject"
3. Enter subject name (e.g., "Mathematics", "Science")
4. Click Save

### Add Questions
1. Click "Questions" in the sidebar
2. Click "Add Question"
3. Fill in the form:
   - **Subject:** Select the subject
   - **Question Text:** Enter the question
   - **Options A-D:** Enter each option
   - **Correct Answer:** Select the correct option
   - **Difficulty:** Choose easy/medium/hard
   - **Explanation:** Add explanation for correct answer
4. Check "Is Active" to enable the question
5. Click Save

### Create an Exam Configuration
1. Click "Exam Configurations" in the sidebar
2. Click "Add Exam Configuration"
3. Fill in the form:
   - **Name:** Exam name
   - **Total Questions:** Number of questions (e.g., 25)
   - **Time Limit:** Minutes allowed (e.g., 15)
   - **Pass Percentage:** Minimum score to pass (e.g., 70)
   - **Questions:** Select questions to include
   - **Is Active:** Check this to make it available
4. Click Save

### View Student Results
1. Click "Student Exams" in the sidebar
2. View list of all exams taken
3. Click on a student exam to see detailed results
4. View individual answers with explanations

---

## 👨‍🎓 Student Guide

### Taking an Exam
1. Go to http://localhost:8000
2. Enter your Full Name
3. Enter your Student ID
4. Click "START EXAM"
5. Answer questions using the radio buttons
6. Use "Previous" and "Next" to navigate
7. Click "Submit Exam" when done
8. Confirm submission
9. View your results and explanations

---

## 🔧 Key Features

### Question Management
- ✅ Add/Edit/Delete questions
- ✅ Filter by subject and difficulty
- ✅ Search questions
- ✅ Mark questions as active/inactive
- ✅ Add explanations for answers

### Exam Configuration
- ✅ Create multiple exams
- ✅ Set question count and time limit
- ✅ Configure pass percentage
- ✅ Select specific questions for each exam

### Student Features
- ✅ Simple login with name and ID
- ✅ Real-time countdown timer
- ✅ Progress bar
- ✅ Auto-submit on time expiry
- ✅ Detailed results with explanations

---

## 📊 Database Models

### Subject
- Store exam topic categories

### Question
- Store multiple-choice questions with options and explanations

### ExamConfig
- Store exam settings and question selections

### StudentExam
- Record of each student's exam session

### StudentAnswer
- Individual answers with correctness tracking

---

## 🛠️ Common Tasks

### Add 25 Questions for an Exam
1. Go to Admin > Questions
2. Add questions one by one
3. Go to Admin > Exam Configurations
4. Create new config and select all 25 questions

### Change Pass Percentage
1. Admin > Exam Configurations
2. Edit the exam
3. Change "Pass Percentage" to desired value
4. Click Save

### View a Student's Exam
1. Admin > Student Exams
2. Click on the student's exam record
3. View all questions and answers

### Disable a Question
1. Admin > Questions
2. Click on the question
3. Uncheck "Is Active"
4. Click Save

---

## ⚙️ Configuration

### Change Exam Time
Edit `cbt_app/views.py` line 70:
```python
TIME_LIMIT = 15 * 60  # Change 15 to desired minutes
```

### Change Exam Name
Admin > Exam Configurations > Edit the name field

### Change Pass Mark
Admin > Exam Configurations > Edit pass_percentage field

---

## 🐛 Troubleshooting

### Port 8000 Already in Use
```bash
python manage.py runserver 8001
```

### Database Issues
```bash
python manage.py migrate --run-syncdb
```

### Can't Login to Admin
```bash
python manage.py changepassword admin
```

### No Questions Showing
Make sure to:
1. Create at least one Question
2. Create an ExamConfig with Is Active checked
3. Add questions to the ExamConfig

---

## 📝 Sample Data

Sample questions are provided in `load_sample_data.py`:
```bash
python manage.py shell < load_sample_data.py
```

This creates:
- 5 Digital Technology questions
- 5 General Knowledge questions
- 1 Active Exam Configuration

---

## 🔐 Security Note

For production use:
1. Change SECRET_KEY in settings.py
2. Set DEBUG = False
3. Use PostgreSQL instead of SQLite
4. Enable HTTPS
5. Set proper ALLOWED_HOSTS

---

## 📞 Support

For issues:
1. Check Django logs in terminal
2. Visit admin panel to verify data
3. Check if ExamConfig is marked as Active
4. Ensure questions are marked as Active

---

Enjoy your CBT Examination System! 🎓
