from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from authentication.models import Profile


class AuthenticationTests(TestCase):
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
        user = User.objects.create_user(username='member', is_active=False)
        user.profile.phone_number = '+254700000000'
        user.profile.save()
        with patch('authentication.tasks.africastalking.initialize'), \
                patch('authentication.tasks.africastalking.SMS') as sms, \
                patch('authentication.tasks.generate_random_code', return_value='123456'):
            sms.send.return_value = {'SMSMessageData': {'Recipients': [{'statusCode': 101}]}}
            send_verification_code_sms(user.pk)
            sms.send.assert_called_once_with('Your verification code is 123456', ['+254700000000'])
            from django.contrib.auth.hashers import check_password
            self.assertTrue(check_password('123456', UserCode.objects.get(user=user).code))


class SignupFlowTests(TestCase):
    def setUp(self):
        self.initialize = patch('authentication.tasks.africastalking.initialize').start()
        self.sms = patch('authentication.tasks.africastalking.SMS').start()
        patch('authentication.tasks.generate_random_code', return_value='123456').start()
        self.addCleanup(patch.stopall)
        self.sms.send.return_value = {'SMSMessageData': {'Recipients': [{'statusCode': 101}]}}
        self.data = {
            'username': 'new_member', 'role': 'mentee', 'phone_number': '+254 700-000-000',
            'password': 'test-password', 'confirm_password': 'test-password',
        }

    def signup(self):
        response = self.client.post(reverse('signup'), self.data)
        self.assertRedirects(response, reverse('verify_account'), fetch_redirect_response=False)
        return User.objects.get(username='new_member')

    def test_mentee_verifies_phone_then_logs_in(self):
        from authentication.models import UserCode
        from django.contrib.auth.hashers import check_password
        user = self.signup()
        self.assertFalse(user.is_active)
        self.assertEqual(user.email, '')
        self.assertEqual(user.profile.phone_number, '+254700000000')
        self.assertNotIn('_auth_user_id', self.client.session)
        code = UserCode.objects.get(user=user)
        self.assertNotEqual(code.code, '123456')
        self.assertTrue(check_password('123456', code.code))
        self.sms.send.assert_called_once_with('Your verification code is 123456', ['+254700000000'])
        self.assertIsNone(authenticate(username=user.username, password='test-password'))
        response = self.client.post(reverse('verify_account'), {'code': '123456'})
        self.assertRedirects(response, reverse('login'))
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertFalse(UserCode.objects.filter(user=user).exists())
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(authenticate(username=user.username, password='test-password'), user)
        self.assertRedirects(self.client.post(reverse('verify_account'), {'code': '123456'}), reverse('signup'))

    def test_mentor_requires_admin_activation(self):
        from authentication.models import UserCode
        self.data.update(role='mentor', email='mentor@example.com', phone_number='')
        response = self.client.post(reverse('signup'), self.data)
        self.assertContains(response, 'awaiting approval')
        user = User.objects.get(username='new_member')
        self.assertEqual(user.profile.role, 'mentor')
        self.assertEqual(user.email, 'mentor@example.com')
        self.assertFalse(user.is_active)
        self.assertFalse(UserCode.objects.filter(user=user).exists())
        self.sms.send.assert_not_called()
        self.assertIsNone(authenticate(username=user.username, password='test-password'))
        admin_user = User.objects.create_superuser('administrator1', 'admin@example.com', 'test-password')
        self.client.force_login(admin_user)
        response = self.client.post(reverse('admin:auth_user_changelist'), {
            'action': 'approve_mentors', '_selected_action': [user.pk],
        })
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(authenticate(username=user.username, password='test-password'), user)

    def test_contact_validation(self):
        from authentication.forms import SignUpForm
        for updates, field in [({'phone_number': ''}, 'phone_number'),
                               ({'phone_number': 'garbage'}, 'phone_number'),
                               ({'role': 'mentor', 'email': ''}, 'email'),
                               ({'role': 'mentor', 'email': 'invalid'}, 'email')]:
            with self.subTest(updates=updates):
                form = SignUpForm({**self.data, **updates})
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)
        self.assertFalse(User.objects.filter(username='new_member').exists())

    def test_duplicate_normalized_phone_rejected(self):
        self.signup()
        response = self.client.post(reverse('signup'), {**self.data, 'username': 'another_member'})
        self.assertContains(response, 'An account with this phone number already exists.')
        self.assertFalse(User.objects.filter(username='another_member').exists())

    def test_wrong_codes_and_attempt_limit(self):
        from authentication.models import UserCode
        user = self.signup()
        for _ in range(5):
            response = self.client.post(reverse('verify_account'), {'code': '654321'})
            self.assertContains(response, 'incorrect')
        self.assertEqual(UserCode.objects.get(user=user).attempts, 5)
        response = self.client.post(reverse('verify_account'), {'code': '123456'})
        self.assertContains(response, 'Too many incorrect attempts')
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_expired_code_and_resend(self):
        from datetime import timedelta
        from django.utils import timezone
        from authentication.models import UserCode
        user = self.signup()
        UserCode.objects.filter(user=user).update(issued_at=timezone.now() - timedelta(minutes=11))
        response = self.client.post(reverse('verify_account'), {'code': '123456'})
        self.assertContains(response, 'expired')
        self.assertRedirects(self.client.post(reverse('verify_account'), {'action': 'resend'}), reverse('verify_account'))
        self.assertEqual(self.sms.send.call_count, 2)
        self.assertEqual(UserCode.objects.get(user=user).attempts, 0)
        self.assertRedirects(self.client.post(reverse('verify_account'), {'code': '123456'}), reverse('login'))

    def test_resend_cooldown(self):
        self.signup()
        response = self.client.post(reverse('verify_account'), {'action': 'resend'}, follow=True)
        self.assertContains(response, 'Please wait a minute')
        self.assertEqual(self.sms.send.call_count, 1)

    def test_sms_failure_keeps_account_inactive_and_allows_retry(self):
        from datetime import timedelta
        from django.utils import timezone
        from authentication.models import UserCode
        self.sms.send.side_effect = RuntimeError('provider unavailable')
        user = self.signup()
        self.assertFalse(user.is_active)
        response = self.client.get(reverse('verify_account'))
        self.assertContains(response, 'We could not send your code')
        UserCode.objects.filter(user=user).update(issued_at=timezone.now() - timedelta(minutes=1))
        self.sms.send.side_effect = None
        self.assertRedirects(self.client.post(reverse('verify_account'), {'action': 'resend'}), reverse('verify_account'))
        self.assertEqual(self.sms.send.call_count, 2)

    def test_verification_requires_signup_session(self):
        from django.test import Client
        self.signup()
        other_browser = Client()
        self.assertRedirects(other_browser.post(reverse('verify_account'), {'code': '123456'}), reverse('signup'))

    def test_profile_forms_do_not_allow_changing_role(self):
        user = User.objects.create_user(username='existing_mentee')
        self.client.force_login(user)
        data = {'first_name': 'Updated', 'bio': 'Learning technology', 'role': 'mentor', 'gender': 'Male',
                'phone_number': '+254700000001', 'mentorship_areas': ['technology'],
                'highest_level_of_study': 'undergraduate'}
        for route in ['initial_setup', 'settings']:
            with self.subTest(route=route):
                response = self.client.post(reverse(route), data)
                self.assertIn(response.status_code, [200, 302])
                user.refresh_from_db()
                self.assertEqual(user.first_name, 'Updated')
                self.assertEqual(user.profile.role, 'mentee')
