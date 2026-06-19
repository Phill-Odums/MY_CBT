#!/usr/bin/env python
"""
CBT Django Setup Verification Script
Run this after setup to verify everything is working correctly.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cbt_project.settings')

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_status(check_name, status, message=""):
    symbol = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} {check_name:<40} {message}")

def check_python_version():
    """Check Python version is 3.8+"""
    version = sys.version_info
    is_valid = version.major >= 3 and version.minor >= 8
    print_status("Python Version", is_valid, f"({version.major}.{version.minor}.{version.micro})")
    return is_valid

def check_django():
    """Check Django installation"""
    try:
        import django
        version = django.get_version()
        print_status("Django Installation", True, f"({version})")
        return True
    except ImportError:
        print_status("Django Installation", False, "(Not installed)")
        return False

def check_database():
    """Check database connection"""
    try:
        django.setup()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_status("Database Connection", True, "(SQLite)")
        return True
    except Exception as e:
        print_status("Database Connection", False, str(e))
        return False

def check_migrations():
    """Check if migrations are applied"""
    try:
        django.setup()
        from django.core.management import call_command
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(django.db.connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print_status("Migrations Applied", False, f"({len(plan)} pending)")
            return False
        else:
            print_status("Migrations Applied", True)
            return True
    except Exception as e:
        print_status("Migrations Applied", False, str(e))
        return False

def check_models():
    """Check if database models exist"""
    try:
        django.setup()
        from cbt_app.models import Subject, Question, ExamConfig, StudentExam, StudentAnswer
        
        subjects = Subject.objects.count()
        questions = Question.objects.count()
        exams = ExamConfig.objects.count()
        
        status = True
        print_status("Subject Model", True, f"({subjects} subjects)")
        print_status("Question Model", True, f"({questions} questions)")
        print_status("ExamConfig Model", True, f"({exams} exam configs)")
        return status
    except Exception as e:
        print_status("Database Models", False, str(e))
        return False

def check_superuser():
    """Check if superuser exists"""
    try:
        django.setup()
        from django.contrib.auth.models import User
        superusers = User.objects.filter(is_superuser=True).count()
        
        if superusers > 0:
            print_status("Superuser Exists", True, f"({superusers} admin user(s))")
            return True
        else:
            print_status("Superuser Exists", False, "(None created)")
            return False
    except Exception as e:
        print_status("Superuser Exists", False, str(e))
        return False

def check_static_files():
    """Check if static files directory exists"""
    static_dir = Path('cbt_app/static')
    css_file = static_dir / 'css' / 'style.css'
    
    if static_dir.exists():
        print_status("Static Directory", True)
        if css_file.exists():
            print_status("CSS File", True)
            return True
        else:
            print_status("CSS File", False)
            return False
    else:
        print_status("Static Directory", False)
        return False

def check_templates():
    """Check if template files exist"""
    templates_dir = Path('cbt_app/templates')
    required_templates = [
        'base.html',
        'login.html',
        'exam.html',
        'submit_exam.html',
        'results.html'
    ]
    
    all_exist = True
    for template in required_templates:
        template_path = templates_dir / template
        exists = template_path.exists()
        print_status(f"Template: {template}", exists)
        all_exist = all_exist and exists
    
    return all_exist

def check_requirements():
    """Check if all required packages are installed"""
    required = {
        'django': 'Django',
        'psycopg2': 'psycopg2',
        'PIL': 'Pillow',
    }
    
    all_installed = True
    for module, name in required.items():
        try:
            __import__(module)
            print_status(f"Package: {name}", True)
        except ImportError:
            print_status(f"Package: {name}", False)
            all_installed = False
    
    return all_installed

def check_settings():
    """Check critical settings"""
    try:
        django.setup()
        from django.conf import settings
        
        debug_ok = settings.DEBUG
        databases_ok = 'default' in settings.DATABASES
        apps_ok = 'cbt_app' in settings.INSTALLED_APPS
        
        print_status("Settings Loaded", True)
        print_status("Debug Mode", debug_ok, f"(DEBUG={debug_ok})")
        print_status("Database Configured", databases_ok)
        print_status("cbt_app Installed", apps_ok)
        
        return debug_ok and databases_ok and apps_ok
    except Exception as e:
        print_status("Settings Check", False, str(e))
        return False

def main():
    print_header("CBT EXAMINATION SYSTEM - VERIFICATION CHECKLIST")
    
    checks = [
        ("Python Version", check_python_version),
        ("Django Installation", check_django),
        ("Django Settings", check_settings),
        ("Database", check_database),
        ("Migrations", check_migrations),
        ("Database Models", check_models),
        ("Superuser", check_superuser),
        ("Requirements", check_requirements),
        ("Static Files", check_static_files),
        ("Templates", check_templates),
    ]
    
    results = []
    for name, check_func in checks:
        print_header(name)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"Error during {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n✓ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Your system is ready.")
        print("\nNext steps:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://localhost:8000")
        print("3. Admin: http://localhost:8000/admin")
        print("4. Load sample data: python manage.py shell < load_sample_data.py")
    else:
        print(f"\n⚠️  {total - passed} check(s) failed.")
        print("\nFailed checks:")
        for name, result in results:
            if not result:
                print(f"  - {name}")
        print("\nSee troubleshooting in README.md")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
