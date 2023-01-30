from django.test import TestCase
from accounts.models import User
from django.contrib.auth import authenticate, login
from emails.tokens import TokenGenerator
import datetime
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.auth.views import PasswordChangeForm, PasswordResetForm
from django.contrib.contenttypes.models import ContentType
from .forms import SignupForm
from django.core import mail
from django.contrib.auth.tokens import default_token_generator

user1_data = {
    'username': 'user1',
    'email': 'user1@example-email.com',
    'password1': 'verysecret1@',
    'password2': 'verysecret1@',
}

user2_data = {
    'username': 'user2',
    'email': 'user2@example-email.com',
    'password1': 'verysecret2@',
    'password2': 'verysecret2@',
}

staff_user_data = {
    'username': 'staff_user',
    'email': 'staff_user@example-email.com',
    'password': 'verysecretstaff_user2@',
}


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

    def test_log_in_and_redirect_to_profile_page(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        response = self.client.post(reverse('accounts:login_user'), self.credentials, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'log in success')
        self.assertRedirects(response, reverse('accounts:profile', kwargs={'pk': response.wsgi_request.user.id}), status_code=302)

    def test_wrong_password(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'wrongpswd'}
        response = self.client.post(reverse('accounts:login_user'), self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response,
                            'Please enter a correct username and password. Note that both fields may be case-sensitive.')


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
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertTemplateUsed('accounts:login_user')
        self.assertContains(response, 'Login', status_code=200)


class EmailRegistrationAndAccountActivationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username=user1_data['username'],
            email=user1_data['email'],
            password=user1_data['password1'],
        )
        self.user.is_active = False
        self.user.save()

        self.staffMember = User.objects.create_user(
            username=staff_user_data['username'],
            email=staff_user_data['email'],
            password=staff_user_data['password'],
        )
        self.staffMember.is_staff = True
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.get(content_type=content_type, codename='register_user')
        self.staffMember.user_permissions.add(permission)
        self.staffMember.save()

    def test_users_with_correct_permissions_can_send_invites_to_app(self):
        self.client.login(
            username=staff_user_data['username'],
            password=staff_user_data['password']
        )
        response = self.client.post(reverse('accounts:signup'), user2_data, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invite sent')

    def test_users_without_correct_permissions_cant_send_invites_to_app(self):
        self.client.login(
            username=user1_data['username'],
            password=user1_data['password1']
        )
        response = self.client.post(reverse('accounts:signup'), user2_data, follow=True)

        self.assertTemplateUsed('accounts:login_user')
        self.assertContains(response, 'Login', status_code=200)

    def test_anonymous_members_cant_access_signup_view(self):
        response = self.client.post(reverse('accounts:signup'), user2_data, follow=True)

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
            'username': user1_data['username'],
            'password': user1_data['password1'],
        }

        response = self.client.post(reverse('accounts:login_user'), user_data, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'log in success')

    def test_inactive_user_cant_login(self):
        user_data = {
            'username': user1_data['username'],
            'password': user1_data['password1'],
        }
        response = self.client.post(reverse('accounts:login_user'), user_data, follow=True)
        self.assertContains(response,
                            'Please enter a correct username and password. Note that both fields may be case-sensitive.')

    def test_registration_token_expired(self):
        self.user.token_generated_timestamp = timezone.now() - datetime.timedelta(days=1)
        self.user.save()

        uid = TokenGenerator().make_uid(self.user)
        token = TokenGenerator().make_token(self.user)
        response = self.client.post(
            reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token}), {}, follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Token expired, ask your manager for new link')


class FormsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username=user1_data['username'],
            email=user1_data['email'],
            password=user1_data['password1'],
        )

    def test_username_has_to_be_present(self):
        user_data = {
            'username': '',
            'email': 'some@email.address',
            'password1': user1_data['password1'],
            'password2': user1_data['password1'],
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='username', errors='This field is required.')
        self.assertFalse(registration_form.is_valid())

    def test_email_addres_has_to_be_present(self):
        user_data = {
            'username': 'testName',
            'email': '',
            'password1': user1_data['password1'],
            'password2': user1_data['password1'],
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='email', errors='This field is required.')
        self.assertFalse(registration_form.is_valid())

    def test_password1_has_to_be_present(self):
        user_data = {
            'username': 'testName',
            'email': 'some@email.address',
            'password1': '',
            'password2': user1_data['password1'],
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='password1', errors='This field is required.')
        self.assertFalse(registration_form.is_valid())

    def test_password2_has_to_be_present(self):
        user_data = {
            'username': 'testName',
            'email': 'some@email.address',
            'password1': user1_data['password1'],
            'password2': '',
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='password2', errors='This field is required.')
        self.assertFalse(registration_form.is_valid())

    def test_passwords_have_to_match(self):
        user_data = {
            'username': 'testName',
            'email': 'some@email.address',
            'password1': user1_data['password1'],
            'password2': 'lorem ipsum',
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='password2', errors='The two password fields didn’t match.')
        self.assertFalse(registration_form.is_valid())

    def test_email_address_has_to_be_valid(self):
        user_data = {
            'username': 'some_other_name',
            'email': 'some_other_name@',
            'password1': user1_data['password1'],
            'password2': user1_data['password1'],
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='email', errors='Enter a valid email address.')
        self.assertFalse(registration_form.is_valid())

    def test_password_cant_be_too_short(self):
        user_data = {
            'username': 'some_other_name',
            'email': 'some@email.address',
            'password1': 'lorem',
            'password2': 'lorem',
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='password2', errors='This password is too short. It must '
                                                                          'contain at least 8 characters.')
        self.assertFalse(registration_form.is_valid())

    def test_password_cant_be_entirely_numeric_and_too_common(self):
        user_data = {
            'username': 'some_other_name',
            'email': 'some@email.address',
            'password1': '12345678',
            'password2': '12345678',
        }
        registration_form = SignupForm(data=user_data)
        self.assertEqual(registration_form.errors['password2'][0], 'This password is too common.')
        self.assertEqual(registration_form.errors['password2'][1], 'This password is entirely numeric.')
        self.assertFalse(registration_form.is_valid())

    def test_password_cant_be_similar_to_other_user_data(self):
        user_data = {
            'username': 'some_other_name',
            'email': 'some@email.address',
            'password1': 'some@email.address',
            'password2': 'some@email.address',
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form,
                             field='password2',
                             errors='The password is too similar to the email address.')
        self.assertFalse(registration_form.is_valid())

    def test_username_has_to_be_valid(self):
        user_data = {
            'username': 't~',
            'email': 'some@email.address',
            'password1': user1_data['password1'],
            'password2': user1_data['password1'],
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form,
                             field='username',
                             errors='Enter a valid username. This value may contain only letters, numbers, '
                                    'and @/./+/-/_ characters.')
        self.assertFalse(registration_form.is_valid())

    def test_email_addres_has_to_be_unique(self):
        user_data = {
            'username': 'some_other_name',
            'email': user1_data['email'],
            'password1': user1_data['password1'],
            'password2': user1_data['password1'],
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='email', errors='User with this Email address already exists.')
        self.assertFalse(registration_form.is_valid())

    def test_username_has_to_be_unique(self):
        user_data = {
            'username': user1_data['username'],
            'email': 'some@email.address',
            'password1': user1_data['password1'],
            'password2': user1_data['password1'],
        }
        registration_form = SignupForm(data=user_data)
        self.assertFormError(registration_form, field='username', errors='A user with that username already exists.')
        self.assertFalse(registration_form.is_valid())

    def test_valid_password_change_form(self):
        pswd_change_data = {
            'old_password': user1_data['password1'],
            'new_password1': 'new_pass+1',
            'new_password2': 'new_pass+1'
        }
        pswd_change_form = PasswordChangeForm(data=pswd_change_data, user=self.user)
        self.assertTrue(pswd_change_form.is_valid())

    def test_old_password_has_to_be_present(self):
        pswd_change_data = {
            'old_password': '',
            'new_password1': 'new_pass+1',
            'new_password2': 'new_pass+1'
        }
        pswd_change_form = PasswordChangeForm(data=pswd_change_data, user=self.user)
        self.assertFormError(pswd_change_form, field='old_password', errors='This field is required.')
        self.assertFalse(pswd_change_form.is_valid())

    def test_old_password_must_match(self):
        pswd_change_data = {
            'old_password': 'lorem ipsum',
            'new_password1': 'new_pass+1',
            'new_password2': 'new_pass+1'
        }
        pswd_change_form = PasswordChangeForm(data=pswd_change_data, user=self.user)
        self.assertFormError(pswd_change_form, field='old_password', errors='Your old password was entered incorrectly. Please enter it again.')
        self.assertFalse(pswd_change_form.is_valid())

    def test_new_passwords_has_to_match(self):
        pswd_change_data = {
            'old_password': user1_data['password1'],
            'new_password1': 'new_pass+1',
            'new_password2': 'new_pass+2'
        }
        pswd_change_form = PasswordChangeForm(data=pswd_change_data, user=self.user)
        self.assertFormError(pswd_change_form, field='new_password2', errors='The two password fields didn’t match.')
        self.assertFalse(pswd_change_form.is_valid())

    def test_new_password_cant_be_blank(self):

        pswd_change_data = {
            'old_password': user1_data['password1'],
            'new_password1': '',
            'new_password2': ''
        }
        pswd_change_form = PasswordChangeForm(data=pswd_change_data, user=self.user)
        self.assertFormError(pswd_change_form, field='new_password1', errors='This field is required.')
        self.assertFalse(pswd_change_form.is_valid())


class TestUserProfilePage(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=user1_data['username'],
            email=user1_data['email'],
            password=user1_data['password1'],
        )

        self.user_can_view_other_users = User.objects.create_user(
            username=user2_data['username'],
            email=user2_data['email'],
            password=user2_data['password1'],
        )

        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.get(content_type=content_type, codename='view_any_user')
        self.user_can_view_other_users.user_permissions.add(permission)
        self.user_can_view_other_users.save()

    def test_not_logged_in_user_cant_access_profile_page(self):
        response = self.client.get(reverse('accounts:profile', kwargs={'pk': 1}), follow=True)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_user_can_view_its_profile_page(self):
        self.client.login(username=user1_data['username'], password=user1_data['password1'])
        response = self.client.get(reverse('accounts:profile', kwargs={'pk': self.user.id}), follow=True)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertEqual(response.context['object'].username, user1_data['username'])

    def test_users_without_correct_permission_cant_view_other_users_profile_page(self):
        self.client.login(username=user1_data['username'], password=user1_data['password1'])
        response = self.client.get(reverse('accounts:profile', kwargs={'pk': self.user_can_view_other_users.id}), follow=True)
        self.assertEqual(response.context['object'].username, self.user.username)
        self.assertNotEqual(response.context['object'].username, self.user_can_view_other_users.username)

    def test_users_with_correct_permission_can_view_other_users_profile_page(self):
        self.client.login(username=user2_data['username'], password=user2_data['password1'])
        response = self.client.get(reverse('accounts:profile', kwargs={'pk': self.user.id}), follow=True)
        self.assertEqual(response.context['object'].username, self.user.username)


class TestUserIndex(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=user1_data['username'],
            email=user1_data['email'],
            password=user1_data['password1'],
        )

        self.user_can_view_index = User.objects.create_user(
            username=user2_data['username'],
            email=user2_data['email'],
            password=user2_data['password1'],
        )

        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.get(content_type=content_type, codename='view_index')
        self.user_can_view_index.user_permissions.add(permission)
        self.user_can_view_index.save()

    def test_anonymous_users_cant_view_users_index(self):
        response = self.client.get(reverse('accounts:index'), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_user_without_correct_permission_cant_view_users_index(self):
        self.client.login(username=user1_data['username'], password=user1_data['password1'])
        response = self.client.get(reverse('accounts:index'), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_user_with_correct_permission_can_view_users_index(self):
        self.client.login(username=user2_data['username'], password=user2_data['password1'])
        response = self.client.get(reverse('accounts:index'), follow=True)

        queryset = [
            User(
                id=self.user.id,
                username=user1_data['username'],
                email=user1_data['email'],
                password=user1_data['password1'],
            ),
            User(
                id=self.user_can_view_index.id,
                username=user2_data['username'],
                email=user2_data['email'],
                password=user2_data['password1'],
            )
        ]

        self.assertQuerysetEqual(response.context['users'], queryset, ordered=False)
        self.assertEqual(response.status_code, 200)

class TestUserPasswordChange(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username=user1_data['username'],
            email=user1_data['email'],
            password=user1_data['password1'],
        )

    def test_not_logged_in_user_cant_access_password_change_page(self):
        response = self.client.get(reverse('password_change'), follow=True)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_logged_in_user_can_access_password_change_page(self):
        self.client.login(username=user1_data['username'], password=user1_data['password1'])
        response = self.client.post(reverse('password_change'), {}, follow=True)
        self.assertContains(response, 'Welcome to the Password Change Page', status_code=200)

    def test_loged_in_user_can_change_password(self):
        self.client.login(username=user1_data['username'], password=user1_data['password1'])
        pswd_change_data = {
            'old_password': user1_data['password1'],
            'new_password1': 'new_pass+1',
            'new_password2': 'new_pass+1'
        }
        response = self.client.post(reverse('password_change'), pswd_change_data, follow=True)
        self.assertRedirects(response, reverse('password_change_done'))
        self.client.logout()

        user = authenticate(username=user1_data['username'], password=user1_data['password1'])
        self.assertFalse(user is not None and user.is_authenticated)
        user = authenticate(username=user1_data['username'], password=pswd_change_data['new_password1'])
        self.assertTrue(user is not None and user.is_authenticated)

    def test_not_logged_in_user_can_access_password_reset_page(self):
        response = self.client.get(reverse('password_reset'))
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

    def test_loged_in_user_can_send_reset_password(self):
        self.client.login(username=user1_data['username'], password=user1_data['password1'])
        response = self.client.post(reverse('password_reset'), {'email': user1_data['email']}, follow=True)
        self.assertRedirects(response, reverse('password_reset_done'), status_code=302)

    def test_not_loged_in_user_can_send_reset_password(self):
        response = self.client.post(reverse('password_reset'), {'email': user1_data['email']}, follow=True)
        self.assertRedirects(response, reverse('password_reset_done'), status_code=302)

    def test_user_can_reset_password_from_link(self):
        new_passwords_dict = {
            'new_password1': 'newSecretP@ssword1',
            'new_password2': 'newSecretP@ssword1'
        }
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

        response = self.client.post(reverse('password_reset'), {'email': self.user.email})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(f'Someone asked for password reset for email {self.user.email}', mail.outbox[0].body)

        token = default_token_generator.make_token(self.user)
        uid = TokenGenerator().make_uid(self.user)

        response = self.client.post(reverse('password_reset_confirm', kwargs={'token': token, 'uidb64': uid}),
                                    new_passwords_dict,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'/accounts/reset/{uid}/set-password/')
        response = self.client.post(f'/accounts/reset/{uid}/set-password/', new_passwords_dict)
        self.assertRedirects(response, reverse('password_reset_complete'))

        user = authenticate(username=user1_data['username'], password=user1_data['password1'])
        self.assertFalse(user is not None and user.is_authenticated)
        user = authenticate(username=user1_data['username'], password=new_passwords_dict['new_password1'])
        self.assertTrue(user is not None and user.is_authenticated)
