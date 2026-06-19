"""
Script to load sample questions into the database.
Run with: python manage.py shell < load_sample_data.py
"""

from cbt_app.models import Subject, Question, ExamConfig

# Clear existing data
print("Clearing existing data...")
Question.objects.all().delete()
Subject.objects.all().delete()
ExamConfig.objects.all().delete()

# Create Subjects
print("Creating subjects...")
digital_tech = Subject.objects.create(
    name="Digital Technology",
    description="Questions about digital technology, programming, and BASIC"
)
general_ks = Subject.objects.create(
    name="General Knowledge",
    description="General computer science knowledge"
)

# Add Digital Technology Questions
print("Adding Digital Technology questions...")
dt_questions = [
    Question.objects.create(
        subject=digital_tech,
        text="A set of instructions given to the computer to solve a problem is called _______",
        option_a="Hardware",
        option_b="Program",
        option_c="Data",
        option_d="Network",
        correct_answer="B",
        difficulty="easy",
        explanation="A program is a set of instructions given to a computer to solve a specific problem."
    ),
    Question.objects.create(
        subject=digital_tech,
        text="Which of the following is not a characteristic of a good program?",
        option_a="Accuracy",
        option_b="Readability",
        option_c="Complexity",
        option_d="Maintainability",
        correct_answer="C",
        difficulty="medium",
        explanation="Complexity is not a characteristic of a good program. Good programs should be simple and easy to understand."
    ),
    Question.objects.create(
        subject=digital_tech,
        text="The ability of a program to be easily modified is called _______",
        option_a="Efficiency",
        option_b="Generality",
        option_c="Maintainability",
        option_d="Accuracy",
        correct_answer="C",
        difficulty="medium"
    ),
    Question.objects.create(
        subject=digital_tech,
        text="The diagrammatic representation of program logic is known as _________",
        option_a="Algorithm",
        option_b="Flowchart",
        option_c="Pseudocode",
        option_d="Source code",
        correct_answer="B",
        difficulty="easy"
    ),
    Question.objects.create(
        subject=digital_tech,
        text="Which of the following is an example of a high-level language?",
        option_a="Machine Code",
        option_b="Python",
        option_c="Binary code",
        option_d="Assembly Code",
        correct_answer="B",
        difficulty="easy"
    ),
]

# Add General Knowledge Questions
print("Adding General Knowledge questions...")
gk_questions = [
    Question.objects.create(
        subject=general_ks,
        text="What does CPU stand for?",
        option_a="Central Process Unit",
        option_b="Central Processing Unit",
        option_c="Computer Processing Unit",
        option_d="Core Processing Unit",
        correct_answer="B",
        difficulty="easy",
        explanation="CPU stands for Central Processing Unit, which is the main component of a computer."
    ),
    Question.objects.create(
        subject=general_ks,
        text="What does RAM stand for?",
        option_a="Random Access Memory",
        option_b="Read Access Memory",
        option_c="Run Access Memory",
        option_d="Rapid Access Memory",
        correct_answer="A",
        difficulty="easy"
    ),
    Question.objects.create(
        subject=general_ks,
        text="Which stores data permanently?",
        option_a="RAM",
        option_b="CPU Cache",
        option_c="Hard Drive",
        option_d="Processor",
        correct_answer="C",
        difficulty="easy"
    ),
    Question.objects.create(
        subject=general_ks,
        text="What does HTML stand for?",
        option_a="Hyper Text Markup Language",
        option_b="High Text Machine Language",
        option_c="Hyper Transfer Markup Language",
        option_d="Home Tool Markup Language",
        correct_answer="A",
        difficulty="easy"
    ),
    Question.objects.create(
        subject=general_ks,
        text="What is the main function of an operating system?",
        option_a="To manage computer hardware and software resources",
        option_b="To compile source code",
        option_c="To connect to the internet",
        option_d="To create graphics",
        correct_answer="A",
        difficulty="medium"
    ),
]

# Create Exam Configuration
print("Creating exam configuration...")
all_questions = dt_questions + gk_questions
exam_config = ExamConfig.objects.create(
    name="IKWUANO CBT Examination",
    total_questions=10,
    time_limit_minutes=15,
    pass_percentage=70,
    is_active=True
)
exam_config.questions.set(all_questions)

print(f"✓ Created {len(dt_questions)} Digital Technology questions")
print(f"✓ Created {len(gk_questions)} General Knowledge questions")
print(f"✓ Created exam configuration with {exam_config.total_questions} questions")
print("\nSample data loaded successfully!")
print("You can now log in to the admin panel and add more questions.")
