from django.test import TestCase
from accounts.models import User
from django.contrib.auth import authenticate
from emails.tokens import TokenGenerator
import datetime
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class SignInTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='12test12',
                                             email='test@example.com')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        user = authenticate(username='test', password='12test12')
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username='wrong', password='12test12')
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_pssword(self):
        user = authenticate(username='test', password='wrong')
        self.assertFalse(user is not None and user.is_authenticated)


class LogInTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

    def test_log_in(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        response = self.client.post(reverse('accounts:login_user'), self.credentials, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'log in success')
        self.assertRedirects(response, reverse('accounts:profile'), status_code=302)

    def test_wrong_password(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secreassasat'}
        response = self.client.post(reverse('accounts:login_user'), self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')



class LogOutTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        self.user = User.objects.create_user(**self.credentials)
        self.user.save()

    def test_logout_logged_in_user(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.post(reverse('accounts:logout_user'), follow=True)
        messages = list(response.context['messages'])
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'log out success')

    def test_logout_not_logged_in_user(self):
        response = self.client.get(reverse('accounts:logout_user'), follow=True)
        # messages = list(response.context['messages'])
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        # self.assertRedirects(response, reverse_lazy('accounts:login_user'))
        self.assertTemplateUsed('accounts:login_user')
        self.assertContains(response, 'Login', status_code=200)

class EmailRegistrationAndAccountActivationTest(TestCase):
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

    staff_user_data = {
        "username": "staff_user",
        "email": "staff_user@example-email.com",
        "password": "verysecretstaff_user2@",
    }

    def setUp(self):
        self.user = User.objects.create_user(
            username=self.user1_data["username"],
            email=self.user1_data["email"],
            password=self.user1_data["password1"],
        )
        self.user.is_active = False
        self.user.save()

        self.staffMember = User.objects.create_user(
            username=self.staff_user_data["username"],
            email=self.staff_user_data["email"],
            password=self.staff_user_data["password"],
        )
        self.staffMember.is_staff = True
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.get(content_type=content_type, codename='register_user')
        self.staffMember.user_permissions.add(permission)
        self.staffMember.save()

    def test_only_staff_members_can_send_invite_to_app(self):
        self.client.login(
            username=self.staff_user_data["username"],
            password=self.staff_user_data["password"]
        )
        response = self.client.post(reverse('accounts:signup'), self.user2_data, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invite sent')

    def test_non_staff_members_cant_access_signup_view(self):
        self.client.login(
            username=self.user1_data["username"],
            password=self.user1_data["password1"]
        )
        response = self.client.post(reverse('accounts:signup'), self.user2_data, follow=True)

        self.assertTemplateUsed('accounts:login_user')
        self.assertContains(response, 'Login', status_code=200)

    def test_anonymous_members_cant_access_signup_view(self):
        response = self.client.post(reverse('accounts:signup'), self.user2_data, follow=True)

        self.assertTemplateUsed('accounts:login_user')
        self.assertContains(response, 'Login', status_code=200)

    def test_user_registration_using_correct_and_unexpired_activation_link(self):
        uid = TokenGenerator().make_uid(self.user)
        token = TokenGenerator().make_token(self.user)
        self.assertFalse(self.user.token_expired())
        response = self.client.post(
            reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token}), {}, follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Thank you for your email confirmation. Now you can login your account.')
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.is_active)

    def test_user_registration_using_incorrect_activation_link(self):
        response = self.client.post(
            reverse('accounts:activate', kwargs={'uidb64': 'lorem', 'token': 'ipsum'}), {}, follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Activation link is invalid!')
        user = User.objects.get(id=self.user.id)
        self.assertFalse(user.is_active)

    def test_active_user_can_login(self):
        uid = TokenGenerator().make_uid(self.user)
        token = TokenGenerator().make_token(self.user)
        activate_link_response = self.client.post(
            reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token}), {}, follow=True
        )
        messages = list(activate_link_response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Thank you for your email confirmation. Now you can login your account.')
        user_data = {
            "username": self.user1_data["username"],
            "password": self.user1_data["password1"],
        }

        response = self.client.post(reverse('accounts:login_user'), user_data, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'log in success')

    def test_inactive_user_cant_login(self):
        user_data = {
            "username": self.user1_data["username"],
            "password": self.user1_data["password1"],
        }
        response = self.client.post(reverse('accounts:login_user'), user_data, follow=True)
        self.assertContains(response, "Please enter a correct username and password. Note that both fields may be case-sensitive.")
        # messages = list(response.context['messages'])
        # self.assertEqual(len(messages), 1)
        # self.assertEqual(str(messages[0]), 'logging in error')

    def test_registration_token_expired(self):
        self.user.token_generated_timestamp = timezone.now() - datetime.timedelta(days=1)
        self.user.save()

        uid = TokenGenerator().make_uid(self.user)
        token = TokenGenerator().make_token(self.user)
        response = self.client.get(
            reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token}), {}, follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Token expired, ask your manager for new link')
