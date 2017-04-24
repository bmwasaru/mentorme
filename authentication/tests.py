from django.contrib.auth.models import User
from django_webtest import WebTest

from authentication.models import Profile


class ProfileCreateWhenUserIsCreated(WebTest):
    """
    Test that a user profile is create on user creation
    """
    def test_user_creation_creates_user_profile(self):
        u = User.objects.create(username="bmwasaru")
        u.save()
        self.assert_(list(Profile.objects.filter(user__username="bmwasaru")))


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
        self.assertIn('/settings/', response.location)
