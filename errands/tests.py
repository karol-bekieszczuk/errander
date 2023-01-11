from django.test import TestCase
from accounts.models import User
from errands.models import Errand
from django.urls import reverse
from .forms import DetailEditForm


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


class ErrandTest(TestCase):

    def setUp(self):
        #set users data
        self.user1_with_errands_data = {
            "username": "user1",
            "email": "user1@example-email.com",
            "password": "verysecret1@"
        }
        self.user2_with_errands_data = {
            "username": "user2",
            "email": "user2@example-email.com",
            "password": "verysecret2@"
        }
        self.user_without_errands_data = {
            "username": "user3",
            "email": "user3@example-email.com",
            "password": "verysecret3@"
        }

        #create users
        self.user1_with_errands = create_user(
            username=self.user1_with_errands_data['username'],
            email=self.user1_with_errands_data['email'],
            password=self.user1_with_errands_data['password']
        )
        self.user2_with_errands = create_user(
            username=self.user2_with_errands_data['username'],
            email=self.user2_with_errands_data['email'],
            password=self.user2_with_errands_data['password']
        )
        self.user_without_errands = create_user(
            username=self.user_without_errands_data['username'],
            email=self.user_without_errands_data['email'],
            password=self.user_without_errands_data['password']
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

    def testUserCanListAssignedErrands(self):
        self.client.login(
            username=self.user1_with_errands_data['username'],
            password=self.user1_with_errands_data['password']
        )
        response = self.client.get(reverse('errands:user_errands'), follow=True)

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

        self.assertQuerysetEqual(list(response.context['user_errands']), queryset)

    def testNotLoggedInUsersCantAccessErrands(self):
        response = self.client.get(reverse('errands:user_errands'), follow=True)
        self.assertTemplateUsed('accounts:login_user')
        self.assertContains(response, 'Login', status_code=200)

    def testUsersWithNoErrandsGetsEmptyQueryset(self):
        self.client.login(
            username=self.user_without_errands_data['username'],
            password=self.user_without_errands_data['password']
        )
        response = self.client.get(reverse('errands:user_errands'), follow=True)
        self.assertQuerysetEqual(response.context['user_errands'], [])
        self.assertContains(response, "No errands assigned.")

    def testUserCanViewDetailsOfErrandHeIsAssignedTo(self):
        self.client.login(
            username=self.user1_with_errands_data['username'],
            password=self.user1_with_errands_data['password']
        )
        user_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        url = reverse('errands:detail', args=(user_errand.id,))
        response = self.client.get(url)
        self.assertContains(response, user_errand.name)

    def testUserCantViewErrandHeIsNotAssignedTo(self):
        self.client.login(
            username=self.user_without_errands_data['username'],
            password=self.user_without_errands_data['password']
        )
        user_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()
        url = reverse('errands:detail', args=(user_errand.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def testUserCanEditErrandHeIsAssignedTo(self):
        self.client.login(
            username=self.user2_with_errands_data['username'],
            password=self.user2_with_errands_data['password']
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

    def testEveryAssignedUserCanSeeChangesToErrand(self):
        user1_errand = Errand.objects.filter(assigned_users=self.user1_with_errands.id).first()

        self.client.login(
            username=self.user1_with_errands_data['username'],
            password=self.user1_with_errands_data['password']
        )
        self.client.post(
            reverse('errands:update', args=(user1_errand.id,)),
            {'status': 2, 'change_reason': 'change by user 1'},
            follow=True
        )

        logout_response = self.client.get(reverse('accounts:logout_user'), follow=True)
        self.assertFalse(logout_response.wsgi_request.user.is_authenticated)

        self.client.login(
            username=self.user2_with_errands_data['username'],
            password=self.user2_with_errands_data['password']
        )

        response = self.client.get(reverse('errands:detail', args=(user1_errand.id,)), follow=True)
        self.assertContains(response, 'change by user 1')

    def testUserCantUpdateErrandWithoutProvidingReason(self):
        errand_details_form_data = {
            'status': 2,
            'change_reason': '',
        }
        details_form = DetailEditForm(data=errand_details_form_data)
        self.assertFalse(details_form.is_valid())

    def testUserCantUpdateErrandWithoutProvidingStatus(self):
        errand_details_form_data = {
            'status': '',
            'change_reason': 'reason',
        }
        details_form = DetailEditForm(data=errand_details_form_data)
        self.assertFalse(details_form.is_valid())
