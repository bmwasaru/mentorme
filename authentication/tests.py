from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.test import Client

from django_webtest import WebTest

from authentication.models import Profile


class Signup(WebTest):

    def test_signup_redirect_to_settings(self):
        signup_page = self.app.get('/signup/')
        signup_form = signup_page.form
        self.assertNotIn(
            'User with this Username already exists.',
            signup_form.text
        )
        signup_form['username'] = 'bmwasaru'
        signup_form['email'] = 'bmwasaru@gmail.com'
        signup_form['password'] = 'u937riehf44'
        signup_form['confirm_password'] = 'u937riehf44'
        response = signup_form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertIn('/settings/', response.location)


class Login(WebTest):
    """Tests for user login and logout"""

    def setUp(self):
        User.objects.create(
            username="bmwasaru", password="u937riehf44", is_active=True)

    def test_login(self):
        user = authenticate(username="bmwasaru", password="u937riehf44")
        self.assertTrue(user and user.is_active)

    def test_logout(self):
        self.client = Client()
        username = "bmwasaru"
        password = "u937riehf44"
        self.client.login(username=username, password=password)
        # check that the user is logged in
        self.assertEqual(1, self.client.session.get('_auth_user_id'))

        # logout the user
        self.client.logout()
        self.assertNotEqual(1, self.client.session.get('_auth_user_id'))
        questions_page = self.app.get('/questions/')
        self.assertIn('Log in', questions_page.content)


class ProfileCreateWhenUserIsCreated(WebTest):
    """
    Test that a user profile is create on user creation
    """

    def test_user_creation_creates_user_profile(self):
        u = User.objects.create(username="bmwasaru")
        u.save()
        self.assert_(list(Profile.objects.filter(user__username="bmwasaru")))
