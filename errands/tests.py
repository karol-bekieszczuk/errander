from django.test import TestCase
from accounts.models import User
from errands.models import Errand
from django.urls import reverse
from .forms import DetailEditForm, CreateErrandForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    return user


def create_errand(name, description, status=1):
    return Errand.objects.create(name=name, description=description, status=status)


def assign_users_to_errands(errands, assigned_users):
    for e in errands:
        for u in assigned_users:
            e.assigned_users.add(u)


#set users data
user1_with_errands_data = {
    "username": "user1",
    "email": "user1@example-email.com",
    "password": "verysecret1@"
}
user2_with_errands_data = {
    "username": "user2",
    "email": "user2@example-email.com",
    "password": "verysecret2@"
}
user3 = {
    "username": "user3",
    "email": "user3@example-email.com",
    "password": "verysecret3@"
}
user_without_errands_data = {
    "username": "user4",
    "email": "user4@example-email.com",
    "password": "verysecret4@"
}
class ErrandTest(TestCase):

    def setUp(self):

        #create users
        self.user1_with_errands = create_user(
            username=user1_with_errands_data['username'],
            email=user1_with_errands_data['email'],
            password=user1_with_errands_data['password']
        )
        self.user2_with_errands = create_user(
            username=user2_with_errands_data['username'],
            email=user2_with_errands_data['email'],
            password=user2_with_errands_data['password']
        )
        self.user_without_errands = create_user(
            username=user_without_errands_data['username'],
            email=user_without_errands_data['email'],
            password=user_without_errands_data['password']
        )
        self.user_with_permission_to_view_and_list_all_errands = create_user(
            username=user3['username'],
            email=user3['email'],
            password=user3['password']
        )

        #create errands with assigned users
        self.errands_with_assigned_user1 = [
            create_errand(
                name='test name1',
                description='test description1'
            ),
            create_errand(
                name='test name2',
                description='test description2'
            )
        ]
        assign_users_to_errands(
            self.errands_with_assigned_user1,
            [
                self.user1_with_errands,
                self.user2_with_errands
            ]
        )

        content_type = ContentType.objects.get_for_model(Errand)
        permission = Permission.objects.get(content_type=content_type, codename='create')
        self.user1_with_errands.user_permissions.add(permission)
        self.user1_with_errands.save()

        permission = Permission.objects.get(content_type=content_type, codename='can_list_and_view_every_errand')
        self.user_with_permission_to_view_and_list_all_errands.user_permissions.add(permission)
        self.user_with_permission_to_view_and_list_all_errands.save()

    def test_user_can_list_assigned_errands(self):
        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )
        response = self.client.get(reverse('errands:index'), follow=True)

        queryset = [
            Errand(
                id=self.errands_with_assigned_user1[0].id,
                name=self.errands_with_assigned_user1[0].name,
                description=self.errands_with_assigned_user1[0].description
            ),
            Errand(
                id=self.errands_with_assigned_user1[1].id,
                name=self.errands_with_assigned_user1[1].name,
                description=self.errands_with_assigned_user1[1].description
            )
        ]

        queryset[0].assigned_users.set([self.user1_with_errands.id])
        queryset[1].assigned_users.set([self.user2_with_errands.id])

        self.assertQuerysetEqual(list(response.context['errands']), queryset)

    def user_without_proper_permission_cant_view_all_errands(self):
        new_errand = create_errand('another', 'errand')
        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )
        response = self.client.get(reverse('errands:index'), follow=True)
        self.assertNotContains(response, new_errand.name)
        self.assertNotEqual(response.context['errands'].count(), Errand.objects.all().count())

    def user_with_proper_permission_can_view_all_errands(self):
        new_errand = create_errand('another', 'errand')
        self.client.login(
            username=user3['username'],
            password=user3['password']
        )
        response = self.client.get(reverse('errands:index'), follow=True)
        self.assertContains(response, new_errand.name)
        self.assertEqual(response.context['errands'].count(), Errand.objects.all().count())

    def test_not_logged_in_users_cant_access_errands(self):
        response = self.client.get(reverse('errands:index'), follow=True)
        self.assertTemplateUsed('accounts:login_user')
        self.assertContains(response, 'Login', status_code=200)

    def test_users_with_no_errands_gets_empty_queryset(self):
        self.client.login(
            username=user_without_errands_data['username'],
            password=user_without_errands_data['password']
        )
        response = self.client.get(reverse('errands:index'), follow=True)
        self.assertQuerysetEqual(response.context['errands'], [])
        self.assertContains(response, "No errands assigned.")

    def test_user_can_view_details_of_errand_he_is_assigned_to(self):
        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )
        user_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        response = self.client.get(reverse('errands:detail', args=(user_errand.id,)), follow=True)

        self.assertEqual(response.context['errand'].name, user_errand.name)

    def test_user_without_proper_permission_cant_view_errand_he_is_not_assigned_to(self):
        self.client.login(
            username=user_without_errands_data['username'],
            password=user_without_errands_data['password']
        )
        user_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        response = self.client.get(reverse('errands:detail', args=(user_errand.id,)), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_user_with_proper_permission_can_view_errand_he_is_not_assigned_to(self):
        self.client.login(
            username=user3['username'],
            password=user3['password']
        )
        user_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        response = self.client.get(reverse('errands:detail', args=(user_errand.id,)), follow=True)

        self.assertEqual(response.context['errand'].name, user_errand.name)

    def test_user_can_edit_errand_he_is_assigned_to(self):
        self.client.login(
            username=user2_with_errands_data['username'],
            password=user2_with_errands_data['password']
        )
        user_errand = Errand.objects.filter(assigned_users=self.user2_with_errands.id).first()

        response = self.client.post(
            reverse('errands:update', args=(user_errand.id,)),
            {'status': 2, 'change_reason': 'test change reason'},
            follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Errand updated')

        user_errand = Errand.objects.get(id=user_errand.id)

        self.assertEqual(user_errand.status, 2)
        self.assertEqual(user_errand.history.first().history_change_reason, 'test change reason')

    def test_every_assigned_user_can_see_changes_to_errand(self):
        user1_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()

        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )
        self.client.post(
            reverse('errands:update', args=(user1_errand.id,)),
            {'status': 2, 'change_reason': 'change by user 1'},
            follow=True
        )

        logout_response = self.client.get(reverse('accounts:logout_user'), follow=True)
        self.assertFalse(logout_response.wsgi_request.user.is_authenticated)

        self.client.login(
            username=user2_with_errands_data['username'],
            password=user2_with_errands_data['password']
        )

        response = self.client.get(reverse('errands:detail', args=(user1_errand.id,)), follow=True)
        self.assertContains(response, 'change by user 1')

    def test_only_users_with_correct_permission_can_create_errands(self):
        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )

        errand_details_form_data = {
            'assigned_users': [self.user1_with_errands.id, ],
            'name': 'errand created with correct permission',
            'description': 'test errand description',
            'address': 'test address',
            'geolocation': '12,124|13.125',
        }
        response = self.client.post(reverse('errands:create'), errand_details_form_data, follow=True)

        self.assertRedirects(response, reverse('errands:detail', kwargs={'pk':response.context['errand'].id}))
        self.assertContains(response, 'errand created with correct permission', status_code=200)

    def test_users_without_correct_permission_cant_create_errands(self):
        self.client.login(
            username=user2_with_errands_data['username'],
            password=user2_with_errands_data['password']
        )

        errand_details_form_data = {
            'assigned_users': [self.user1_with_errands.id, ],
            'name': 'errand created with correct permission',
            'description': 'test errand description',
            'address': 'test address',
            'geolocation': '12,124|13.125',
        }
        response = self.client.post(reverse('errands:create'), errand_details_form_data, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_users_with_correct_permission_can_view_assign_users_checkboxes_in_edit_view(self):
        content_type = ContentType.objects.get_for_model(Errand)
        permission = Permission.objects.get(content_type=content_type, codename='assign_users')
        self.user1_with_errands.user_permissions.add(permission)
        self.user1_with_errands.save()

        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )
        user1_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        response = self.client.get(reverse('errands:detail', args=(user1_errand.id,)), follow=True)
        for u in User.objects.all():
            self.assertContains(response, u.username, status_code=200, count=1)

    def test_users_without_correct_permission_cant_view_users_to_assign(self):
        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )
        user1_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        response = self.client.get(reverse('errands:detail', args=(user1_errand.id,)), follow=True)
        for u in User.objects.all():
            self.assertNotContains(response, u.username, status_code=200)

    def test_users_with_correct_permission_can_assign_users_to_errand(self):
        content_type = ContentType.objects.get_for_model(Errand)
        permission = Permission.objects.get(content_type=content_type, codename='assign_users')
        self.user1_with_errands.user_permissions.add(permission)
        self.user1_with_errands.save()

        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )

        self.assertEqual(self.user_without_errands.errand_set.count(), 0)

        user1_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        response = self.client.post(
            reverse('errands:update', args=(user1_errand.id,)),
            {'status': 2,
             'change_reason': 'added user_without_errands',
             'assigned_users':[self.user1_with_errands.id, self.user2_with_errands.id, self.user_without_errands.id,]},
            follow=True
        )

        self.assertRedirects(response, reverse('errands:detail', args={response.context['errand'].id}), status_code=302)
        self.assertEqual(self.user_without_errands.errand_set.count(), 1)
        self.assertContains(response, 'added user_without_errands')

    def test_users_with_correct_permission_can_remove_users_from_errand(self):
        content_type = ContentType.objects.get_for_model(Errand)
        permission = Permission.objects.get(content_type=content_type, codename='assign_users')
        self.user1_with_errands.user_permissions.add(permission)
        self.user1_with_errands.save()

        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )

        self.assertEqual(self.user2_with_errands.errand_set.count(), 2)

        user2_errand = Errand.objects.filter(assigned_users=self.user2_with_errands.id).first()

        response = self.client.post(
            reverse('errands:update', args=(user2_errand.id,)),
            {'status': 2, 'change_reason': 'removed user 2 with errands', 'assigned_users':[self.user1_with_errands.id]},
            follow=True
        )

        self.assertRedirects(response, reverse('errands:detail', args={response.context['errand'].id}), status_code=302)
        self.assertEqual(self.user2_with_errands.errand_set.count(), 1)
        self.assertNotIn(self.user2_with_errands.username, str(user2_errand.assigned_users.all()))

    def test_users_without_correct_permission_cant_assign_users_to_errand(self):
        self.client.login(
            username=user1_with_errands_data['username'],
            password=user1_with_errands_data['password']
        )

        user1_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        response = self.client.post(
            reverse('errands:update', args=(user1_errand.id,)),
            {'status': 2, 'change_reason': 'errand updated but user not assigned', 'assigned_users':[self.user_without_errands.id]},
            follow=True
        )
        self.assertRedirects(response, reverse('errands:detail', args={response.context['errand'].id}), status_code=302)
        self.assertEqual(self.user_without_errands.errand_set.count(), 0)
        self.assertContains(response, 'errand updated but user not assigned')

class FormsTest(TestCase):

    def setUp(self):

        # create users
        self.user1 = create_user(
            username=user1_with_errands_data['username'],
            email=user1_with_errands_data['email'],
            password=user1_with_errands_data['password']
        )

        self.user_with_add_user_perm = create_user(
            username=user2_with_errands_data['username'],
            email=user2_with_errands_data['email'],
            password=user2_with_errands_data['password']
        )

        self.user_with_create_errand_perm = create_user(
            username=user_without_errands_data['username'],
            email=user_without_errands_data['email'],
            password=user_without_errands_data['password']
        )

        self.errands_with_assigned_user1 = [
            create_errand(
                name='test name1',
                description='test description1'
            ),
            create_errand(
                name='test name2',
                description='test description2'
            )
        ]
        assign_users_to_errands(
            self.errands_with_assigned_user1,
            [
                self.user1,
            ]
        )

        self.user_with_add_user_perm.is_staff = True
        content_type = ContentType.objects.get_for_model(Errand)
        permission = Permission.objects.get(content_type=content_type, codename='assign_users')
        self.user_with_add_user_perm.user_permissions.add(permission)
        self.user_with_add_user_perm.save()

    def test_correctly_filled_out_creation_form_is_valid(self):
        errand_details_form_data = {
            'assigned_users': [self.user1.id, ],
            'name': 'test name',
            'description': 'test errand description',
            'address': 'test address',
            'geolocation': '12,124|13.125',
        }
        form = CreateErrandForm(errand_details_form_data)
        self.assertTrue(form.is_valid())

    def test_create_form_without_assigned_users_is_valid(self):
        errand_details_form_data = {
            'assigned_users': [],
            'name': 'test name',
            'description': 'test errand description',
            'address': 'test address',
            'geolocation': '12,124|13.125',
        }
        form = CreateErrandForm(errand_details_form_data)
        self.assertTrue(form.is_valid())

    def test_create_form_without_name_is_not_valid(self):
        errand_details_form_data = {
            'assigned_users': [self.user1.id, ],
            'name': '',
            'description': 'test errand description',
            'address': 'test address',
            'geolocation': '12,124|13.125',
        }
        form = CreateErrandForm(errand_details_form_data)
        self.assertFormError(form, field='name', errors='This field is required.')
        self.assertFalse(form.is_valid())

    def test_create_form_without_description_is_not_valid(self):
        errand_details_form_data = {
            'assigned_users': [self.user1.id, ],
            'name': 'test name',
            'description': '',
            'address': 'test address',
            'geolocation': '12,124|13.125',
        }
        form = CreateErrandForm(errand_details_form_data)
        self.assertFormError(form, field='description', errors='This field is required.')
        self.assertFalse(form.is_valid())

    def test_create_form_without_address_is_not_valid(self):
        errand_details_form_data = {
            'assigned_users': [self.user1.id, ],
            'name': 'test name',
            'description': 'test errand description',
            'address': '',
            'geolocation': '12,124|13.125',
        }
        form = CreateErrandForm(errand_details_form_data)
        self.assertFormError(form, field='address', errors='This field is required.')
        self.assertFalse(form.is_valid())

    def test_create_form_without_geolocation_is_not_valid(self):
        errand_details_form_data = {
            'assigned_users': [self.user1.id, ],
            'name': 'test name',
            'description': 'test errand description',
            'address': 'test address',
            'geolocation': '',
        }
        form = CreateErrandForm(errand_details_form_data)
        self.assertFormError(form, field='geolocation', errors='This field is required.')
        self.assertFalse(form.is_valid())

    def test_correctly_filled_out_edit_form_is_valid(self):
        errand_details_form_data = {
            'status': 1,
            'change_reason': 'edit',
            'assigned_users': [self.user1.id, ],
        }
        form = DetailEditForm(data=errand_details_form_data, for_user=self.user_with_add_user_perm)
        self.assertTrue(form.is_valid())

    def test_assigned_users_are_not_needed_for_edit_form_to_be_valid(self):
        errand_details_form_data = {
            'status': 1,
            'change_reason': 'edit',
            'assigned_users': [],
        }
        form = DetailEditForm(data=errand_details_form_data, for_user=self.user_with_add_user_perm)
        self.assertTrue(form.is_valid())

    def test_user_cant_update_errand_without_providing_reason(self):
        errand_details_form_data = {
            'status': 2,
            'change_reason': '',
            'assigned_users': [self.user1.id, ],
        }
        details_form = DetailEditForm(data=errand_details_form_data)
        self.assertFormError(details_form, field='change_reason', errors='This field is required.')
        self.assertFalse(details_form.is_valid())

    def test_user_cant_update_errand_without_providing_status(self):
        errand_details_form_data = {
            'status': '',
            'change_reason': 'reason',
            'assigned_users': [self.user1.id, ],
        }
        details_form = DetailEditForm(data=errand_details_form_data)
        self.assertFormError(details_form, field='status', errors='This field is required.')
        self.assertFalse(details_form.is_valid())

    def test_user_cant_assign_users_without_proper_permission_but_form_remains_valid(self):
        errand_details_form_data = {
            'status': 3,
            'change_reason': 'assign user',
            'assigned_users': [self.user1.id, ],
        }
        details_form = DetailEditForm(data=errand_details_form_data, for_user=self.user1)
        self.assertNotIn('assigned_users', details_form.fields.keys())
        self.assertTrue(details_form.is_valid())

    def test_user_with_proper_permission_can_assign_users(self):
        errand_details_form_data = {
            'status': 3,
            'change_reason': 'assign user',
            'assigned_users': [self.user1.id, ],
        }
        details_form = DetailEditForm(data=errand_details_form_data, for_user=self.user_with_add_user_perm)
        self.assertIn('assigned_users', details_form.fields.keys())
        self.assertTrue(details_form.is_valid())
