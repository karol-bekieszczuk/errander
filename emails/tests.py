from django.test import TestCase
from .tokens import TokenGenerator
from django.contrib.auth.models import User


class EmailRegistrationTest(TestCase):
    user1_data = {
        "username": "user1",
        "email": "user1@example-email.com",
        "password1": "verysecret1@",
        "password2": "verysecret1@",
    }

    user2_data = {
        "username": "user2",
        "email": "user2@example-email.com",
        "password1": "verysecret2@",
        "password2": "verysecret2@",
    }

    def setUp(self):
        self.user = User.objects.create_user(
            username=self.user1_data["username"],
            email=self.user1_data["email"],
            password=self.user1_data["password1"],
        )
        self.user.is_active = False
        self.user.save()

    def test_sending_email(self):
        response = self.client.post("/register/signup/", self.user2_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Please confirm your email address to complete the registration")

    def test_user_registration_using_correct_activation_link(self):
        uid = TokenGenerator().make_uid(self.user)
        token = TokenGenerator().make_token(self.user)
        response = self.client.get(f"http://127.0.0.1:8000/register/activate/{uid}/{token}", {})
        self.assertEqual(response.content, b"Thank you for your email confirmation. Now you can login your account.")
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.is_active)

    def test_user_registration_using_incorrect_activation_link(self):
        response = self.client.get("http://127.0.0.1:8000/register/activate/lorem/ipsum", {})
        self.assertEqual(response.content, b"Activation link is invalid!")
        user = User.objects.get(id=self.user.id)
        self.assertFalse(user.is_active)

    def test_active_user_can_login(self):
        uid = TokenGenerator().make_uid(self.user)
        token = TokenGenerator().make_token(self.user)
        self.client.get(f"http://127.0.0.1:8000/register/activate/{uid}/{token}", {})

        user_data = {
            "username": self.user1_data["username"],
            "password": self.user1_data["password1"],
        }
        response = self.client.post('/accounts/login_user/', user_data, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'log in success')

    def test_inactive_user_cant_login(self):
        user_data = {
            "username": self.user1_data["username"],
            "password": self.user1_data["password1"],
        }
        response = self.client.post('/accounts/login_user/', user_data, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'logging in error')
