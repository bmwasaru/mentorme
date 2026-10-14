from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from authentication.models import Profile


class AuthenticationTests(TestCase):
    def test_signup_creates_user_and_profile(self):
        response = self.client.post(reverse('signup'), {
            'username': 'new_member', 'email': 'member@example.com',
            'role': 'mentee', 'password': 'a-long-test-password',
            'confirm_password': 'a-long-test-password',
        })
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='new_member')
        self.assertEqual(user.profile.role, 'mentee')
        self.assertTrue(user.check_password('a-long-test-password'))

    def test_login(self):
        user = User.objects.create_user(username='member', password='test-password')
        self.assertEqual(authenticate(username='member', password='test-password'), user)
        response = self.client.post(reverse('login'), {
            'username': 'member', 'password': 'test-password',
        })
        self.assertRedirects(response, reverse('initial_setup'), fetch_redirect_response=False)
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    def test_logout_requires_post(self):
        user = User.objects.create_user(username='member', password='test-password')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(self.client.post(reverse('logout')), '/')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(self.client.get(reverse('questions')), '/?next=/questions/')

    def test_user_creation_creates_profile(self):
        user = User.objects.create_user(username='member')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_activation_token_invalid_after_confirmation(self):
        from authentication.tokens import account_activation_token
        user = User.objects.create_user(username='member')
        token = account_activation_token.make_token(user)
        self.assertTrue(account_activation_token.check_token(user, token))
        user.profile.email_confirmed = True
        user.profile.save()
        self.assertFalse(account_activation_token.check_token(user, token))

    def test_sms_task_with_current_sdk(self):
        from authentication.models import UserCode
        from authentication.tasks import send_verification_code_sms
        from mentorme import celery_app
        celery_app.autodiscover_tasks(force=True)
        user = User.objects.create_user(username='member')
        user.profile.phone_number = '+254700000000'
        user.profile.save()
        with patch('authentication.tasks.africastalking.initialize'), \
                patch('authentication.tasks.africastalking.SMS') as sms, \
                patch('authentication.tasks.generate_random_code', return_value='123456'):
            sms.send.return_value = {'SMSMessageData': {'Recipients': [{'statusCode': 101}]}}
            send_verification_code_sms(user)
            sms.send.assert_called_once_with('Your verification code is 123456', ['+254700000000'])
            self.assertEqual(UserCode.objects.get(user=user).code, '123456')
