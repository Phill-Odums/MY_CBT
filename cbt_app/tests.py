from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from .forms import StaffRegistrationForm
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
