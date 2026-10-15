from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from activities.models import Notification
from authentication.models import Connection


class MentorshipNotificationTests(TestCase):
    def setUp(self):
        self.mentee = User.objects.create_user(username='mentee', email='mentee@example.com')
        self.mentor = User.objects.create_user(username='mentor', email='mentor@example.com')
        self.mentor.profile.role = 'mentor'
        self.mentor.profile.save()
        self.other_mentor = User.objects.create_user(username='another_mentor')
        self.other_mentor.profile.role = 'mentor'
        self.other_mentor.profile.save()
        self.client.force_login(self.mentee)

    @patch('mentoring.views.send_mail')
    def test_request_creates_one_notification_and_deduplicates_submissions(self, send_mail):
        data = {'to': self.mentor.username, 'message': 'Please mentor me'}
        response = self.client.post(reverse('make_connection'), data)
        self.assertRedirects(response, reverse('u_profile', args=[self.mentor.username]))
        connection = Connection.objects.get()
        notification = Notification.objects.get(notification_type=Notification.MENTORSHIP_REQUESTED)
        self.assertEqual(notification.to_user, self.mentor)
        self.assertEqual(notification.from_user, self.mentee)
        self.assertEqual(notification.connection, connection)
        self.client.post(reverse('make_connection'), data)
        self.assertEqual(Connection.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)
        send_mail.assert_called_once()
        self.client.force_login(self.mentor)
        response = self.client.get(reverse('mentoring'))
        self.assertContains(response, reverse('respond_connection', args=[connection.pk]))
        self.assertContains(response, 'Accept request')

    def test_accept_and_decline_notify_the_correct_mentee(self):
        for decision, status, kind in [
            ('accept', Connection.ACCEPTED, Notification.MENTORSHIP_ACCEPTED),
            ('decline', Connection.DECLINED, Notification.MENTORSHIP_DECLINED),
        ]:
            with self.subTest(decision=decision):
                connection = Connection.objects.create(user=self.mentee, mentor=self.mentor.pk)
                self.client.force_login(self.mentor)
                url = reverse('respond_connection', args=[connection.pk])
                self.assertRedirects(self.client.post(url, {'decision': decision}), reverse('mentoring'))
                connection.refresh_from_db()
                self.assertEqual(connection.status, status)
                notification = Notification.objects.get(connection=connection)
                self.assertEqual(notification.notification_type, kind)
                self.assertEqual(notification.from_user, self.mentor)
                self.assertEqual(notification.to_user, self.mentee)
                self.client.post(url, {'decision': decision})
                self.assertEqual(Notification.objects.filter(connection=connection).count(), 1)
                self.client.force_login(self.mentee)
                self.assertEqual(self.client.post(reverse('open_notification', args=[notification.pk])).status_code, 302)
        response = self.client.get(reverse('connections'))
        self.assertContains(response, self.mentor.username)

    def test_only_assigned_mentor_can_respond(self):
        connection = Connection.objects.create(user=self.mentee, mentor=self.mentor.pk)
        url = reverse('respond_connection', args=[connection.pk])
        self.assertEqual(self.client.post(url, {'decision': 'accept'}).status_code, 403)
        self.client.force_login(self.other_mentor)
        self.assertEqual(self.client.post(url, {'decision': 'accept'}).status_code, 404)
        self.client.force_login(self.mentor)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {'decision': 'unknown'}).status_code, 400)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.mentor)
        self.assertEqual(client.post(url, {'decision': 'accept'}).status_code, 403)
        connection.refresh_from_db()
        self.assertEqual(connection.status, Connection.PENDING)
        self.assertFalse(Notification.objects.exists())

    @patch('mentoring.views.send_mail', side_effect=RuntimeError('mail unavailable'))
    def test_mail_failure_does_not_lose_request_or_notification(self, send_mail):
        with self.assertLogs('mentoring.views', level='WARNING'):
            response = self.client.post(reverse('make_connection'), {
                'to': self.mentor.username, 'message': 'Please mentor me',
            })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Connection.objects.filter(mentor=self.mentor.pk).exists())
        self.assertTrue(Notification.objects.filter(to_user=self.mentor).exists())

    def test_invalid_request_does_not_create_notifications(self):
        url = reverse('make_connection')
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {'to': self.mentor.username, 'message': ''}).status_code, 400)
        self.mentor.is_active = False
        self.mentor.save()
        self.assertEqual(self.client.post(url, {'to': self.mentor.username, 'message': 'Hello'}).status_code, 404)
        self.client.force_login(self.other_mentor)
        self.assertEqual(self.client.post(url, {'to': self.mentee.username, 'message': 'Hello'}).status_code, 403)
        self.assertFalse(Notification.objects.exists())


class MentorApprovalNotificationTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin1', 'admin@example.com', 'password')
        self.mentor = User.objects.create_user(username='pending_mentor', is_active=False)
        self.mentor.profile.role = 'mentor'
        self.mentor.profile.save()
        self.mentee = User.objects.create_user(username='pending_mentee', is_active=False)
        self.client.force_login(self.admin_user)

    def test_bulk_approval_notifies_only_newly_approved_mentors_once(self):
        data = {'action': 'approve_mentors', '_selected_action': [self.mentor.pk, self.mentee.pk]}
        self.client.post(reverse('admin:auth_user_changelist'), data)
        self.client.post(reverse('admin:auth_user_changelist'), data)
        notification = Notification.objects.get(notification_type=Notification.MENTOR_APPROVED)
        self.assertEqual(notification.to_user, self.mentor)
        self.assertEqual(notification.from_user, self.admin_user)
        self.mentor.refresh_from_db()
        self.mentee.refresh_from_db()
        self.assertTrue(self.mentor.is_active)
        self.assertFalse(self.mentee.is_active)
        self.client.force_login(self.mentor)
        self.assertContains(self.client.get(reverse('notifications')), 'approved your mentor account')
        self.assertRedirects(self.client.post(reverse('open_notification', args=[notification.pk])), reverse('mentoring'))

    def test_editing_active_checkbox_also_notifies_once(self):
        modeladmin = admin.site._registry[User]
        request = RequestFactory().post('/')
        request.user = self.admin_user
        self.mentor.is_active = True
        modeladmin.save_model(request, self.mentor, None, change=True)
        modeladmin.save_model(request, self.mentor, None, change=True)
        self.assertEqual(Notification.objects.filter(to_user=self.mentor,
                         notification_type=Notification.MENTOR_APPROVED).count(), 1)
