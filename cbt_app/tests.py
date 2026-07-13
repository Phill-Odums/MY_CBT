from types import SimpleNamespace

import json

from django.conf import settings
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import StaffRegistrationForm
from .models import ExamConfig, Question, StaffCourse, StaffProfile, StaffStudentExam, StudentAnswer, StudentExam, Subject
from .views import build_question_payload


class QuestionPayloadTests(SimpleTestCase):
    def test_build_question_payload_includes_options_and_saved_answer(self):
        question = SimpleNamespace(
            id=7,
            text='What is 2 + 2?',
            option_a='3',
            option_b='4',
            option_c='5',
            option_d='6',
        )

        payload = build_question_payload([question], {7: 'B'})

        self.assertEqual(payload[0]['id'], 7)
        self.assertEqual(payload[0]['text'], 'What is 2 + 2?')
        self.assertEqual(payload[0]['selected_answer'], 'B')
        self.assertEqual([option['value'] for option in payload[0]['options']], ['A', 'B', 'C', 'D'])
        self.assertEqual(payload[0]['options'][1]['text'], '4')


class StaffRegistrationFormTests(TestCase):
    def test_password_must_meet_strength_requirements(self):
        form = StaffRegistrationForm(data={
            'username': 'newstaff',
            'email': 'newstaff@example.com',
            'first_name': 'New',
            'last_name': 'Staff',
            'password': 'weakpass',
            'password_confirm': 'weakpass',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('Password must be 8 to 16 characters long and include at least one uppercase letter, one number, and one symbol.', form.errors['password'])

    def test_password_with_complexity_is_accepted(self):
        form = StaffRegistrationForm(data={
            'username': 'newstaff2',
            'email': 'newstaff2@example.com',
            'first_name': 'New',
            'last_name': 'Staff',
            'password': 'StrongPass1!',
            'password_confirm': 'StrongPass1!',
        })

        self.assertTrue(form.is_valid(), form.errors)


class ExamProgressViewTests(TestCase):
    def _seed_session(self, **session_data):
        session = self.client.session
        for key, value in session_data.items():
            session[key] = value
        session.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key
        self.client.cookies[settings.SESSION_COOKIE_NAME]['path'] = '/'
        self.client.cookies[settings.SESSION_COOKIE_NAME]['domain'] = 'testserver'

    def setUp(self):
        self.exam_config = ExamConfig.objects.create(
            name='Demo Exam',
            total_questions=5,
            time_limit_minutes=10,
            pass_percentage=70,
        )
        self.exam = StudentExam.objects.create(
            student_name='Jane Doe',
            student_id='S001',
            exam_config=self.exam_config,
        )

        self.user = User.objects.create_user(username='staffuser', password='StrongPass1!')
        self.staff_profile = StaffProfile.objects.create(user=self.user)
        self.staff_course = StaffCourse.objects.create(
            staff=self.staff_profile,
            course_name='Course One',
            registration_code='ABC123',
            total_questions=5,
            time_limit_minutes=8,
            pass_percentage=70,
        )
        self.staff_exam = StaffStudentExam.objects.create(
            course=self.staff_course,
            student_name='John Doe',
            student_id='S002',
            total_questions=5,
        )

    def test_exam_progress_accepts_get_requests_and_returns_time_data(self):
        self._seed_session(
            exam_id=self.exam.id,
            question_ids=[1, 2],
            exam_start_time=timezone.now().isoformat(),
            time_limit_minutes=10,
        )

        response = self.client.get(reverse('cbt:exam_progress'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('time_remaining', payload)
        self.assertIn('time_expired', payload)
        self.assertFalse(payload['time_expired'])
        self.assertRegex(payload['time_remaining'], r'^\d{2}:\d{2}$')

    def test_exam_progress_rejects_non_get_requests(self):
        self._seed_session(
            exam_id=self.exam.id,
            question_ids=[1, 2],
            exam_start_time=timezone.now().isoformat(),
            time_limit_minutes=10,
        )

        response = self.client.post(reverse('cbt:exam_progress'))

        self.assertEqual(response.status_code, 405)

    def test_staff_exam_progress_accepts_get_requests(self):
        self._seed_session(
            staff_exam_id=self.staff_exam.id,
            staff_question_ids=[1, 2],
            staff_exam_start_time=timezone.now().isoformat(),
        )

        response = self.client.get(reverse('cbt:exam_progress'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('time_remaining', payload)
        self.assertIn('time_expired', payload)
        self.assertFalse(payload['time_expired'])

    def test_exam_progress_returns_expired_payload_when_no_active_session(self):
        response = self.client.get(reverse('cbt:exam_progress'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['time_expired'])
        self.assertEqual(payload['time_remaining'], '00:00')

    def test_staff_login_uses_isolated_session_state_without_clobbering_exam_data(self):
        self._seed_session(
            exam_id=self.exam.id,
            student_name='Jane Doe',
            student_id='S001',
        )

        response = self.client.post(reverse('cbt:staff_login'), {
            'username': 'staffuser',
            'password': 'StrongPass1!',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['staff_auth_user_id'], self.user.id)
        self.assertEqual(self.client.session['exam_id'], self.exam.id)
        self.assertEqual(self.client.session['student_name'], 'Jane Doe')

    def test_submit_exam_uses_client_answers_payload_for_grading(self):
        subject = Subject.objects.create(name='Math')
        question = Question.objects.create(
            subject=subject,
            text='What is 2 + 2?',
            option_a='4',
            option_b='5',
            option_c='6',
            option_d='7',
            correct_answer='A',
            is_active=True,
        )
        self.exam.total_questions = 1
        self.exam.save(update_fields=['total_questions'])

        self._seed_session(
            exam_id=self.exam.id,
            question_ids=[question.id],
            exam_start_time=timezone.now().isoformat(),
            time_limit_minutes=10,
        )

        response = self.client.post(
            reverse('cbt:submit_exam'),
            {
                'confirm': 'on',
                'answers_payload': json.dumps({str(question.id): 'A'}),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.status, 'graded')
        self.assertEqual(self.exam.score, 1)
        answer = StudentAnswer.objects.get(exam=self.exam, question=question)
        self.assertEqual(answer.selected_answer, 'A')
