from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


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
        response = self.client.post('/accounts/login_user/', self.credentials, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'log in success')
    def test_wrong_pssword(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secreassasat'}
        response = self.client.post('/accounts/login_user/', self.credentials, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'logging in error')


class LogOutTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        self.user = User.objects.create_user(**self.credentials)
        self.user.save()

    def test_logout_logged_in_user(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.post('/accounts/logout_user/', follow=True)
        messages = list(response.context['messages'])
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'log out success')

    def test_logout_not_logged_in_user(self):
        response = self.client.post('/accounts/logout_user/', follow=True)
        messages = list(response.context['messages'])
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'you are not logged in')
