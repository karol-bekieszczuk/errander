from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class SignTest(TestCase):
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
