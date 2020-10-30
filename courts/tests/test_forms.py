from django.test import TestCase
from ..models import Signup
from ..forms import EmailSignupForm
from http import HTTPStatus


class SignUpFormTest(TestCase):

    def create_signup(self, email):
        signup = Signup()
        signup.email = email
        signup.save()

    # https://docs.djangoproject.com/en/3.1/topics/testing/tools/#testcase
    @classmethod
    def setUpTestData(cls):
        cls.email = 'bobsmith@gmail.com'

    # https://stackoverflow.com/a/7304658
    def test_sign_up(self):
        form = EmailSignupForm(data={'email': self.email})
        self.assertTrue(form.is_valid())

    def test_email_already_exists(self):
        self.create_signup(self.email)

        duplicate_form = EmailSignupForm(data={'email': self.email})
        self.assertFalse(duplicate_form.is_valid())

    # https://stackoverflow.com/a/55356656
    def test_email_exists_message(self):
        self.create_signup(self.email)

        duplicate_form = EmailSignupForm(data={'email': self.email})

        error_message = 'Signup with this Email already exists.'
        self.assertIn(error_message, duplicate_form.errors['email'])

    # https://adamj.eu/tech/2020/06/15/how-to-unit-test-a-django-form/
    def test_html_get(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        random_html = '<div class="control has-icons-left">'
        self.assertContains(response, random_html, html=False)

    def test_html_post_success(self):
        response = self.client.post("", data={'email': self.email})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request.get('PATH_INFO'), "")
