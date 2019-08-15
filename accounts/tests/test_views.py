from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.urls import reverse


from ..views import UserLoginView


class LoginViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='john', email='john.smith@exampl.com',
                                             password='topsecret')
        g = Group.objects.create(name='verbalisant')
        g.user_set.add(self.user)

        pass

    def tearDown(self):
        pass

    def test_login_url_resolves_to_correct_view(self):
        # Create an instance of get request
        request = self.factory.get('/accounts/login')
        request.user = self.user
        response = UserLoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_login_reverse_name_resolves_to_correct_view(self):
        # Create an instance of get request
        request = self.factory.get(reverse('accounts:login'))
        request.user = self.user
        response = UserLoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_login_with_username_and_password(self):
        data = {'username': 'john', 'password': 'topsecret'}
        request = self.factory.post(reverse('accounts:login'), data=data)
        #request.user = self.user
        response = UserLoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        #print(request)


class LogoutViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='john', email='john.smith@exampl.com',
                                             password='topsecret')

    def tearDown(self):
        pass

    def test_logout_url_resolves_to_correct_view(self):
        # Create an instance of get request
        request = self.factory.get('/accounts/logouxt')
        request.user = self.user
        response = UserLoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        #self.assertRedirects(response, reverse('accounts:login'))

    def test_logout_reverse_name_resolves_to_correct_view(self):
        # Create an instance of get request
        request = self.factory.get(reverse('accounts:logout'))
        request.user = self.user
        response = UserLoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        #self.assertRedirects(response, reverse('accounts:login'))

