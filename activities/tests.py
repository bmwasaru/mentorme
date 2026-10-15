from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from activities.models import Notification
from questions.models import Answer, Question


class NotificationTests(TestCase):
    def setUp(self):
        self.recipient = User.objects.create_user(username='recipient')
        self.actor = User.objects.create_user(username='actor', first_name='Brian', last_name='Mwachofi')
        self.outsider = User.objects.create_user(username='outsider')
        self.question = Question.objects.create(user=self.recipient, title='A question', category='technology')
        self.answer = Answer.objects.create(user=self.actor, question=self.question, description='An answer')
        self.notification = Notification.objects.create(
            from_user=self.actor, to_user=self.recipient, notification_type=Notification.ANSWERED,
            question=self.question, answer=self.answer,
        )
        self.client.force_login(self.recipient)

    def test_browsing_and_preview_do_not_mark_read(self):
        response = self.client.get(reverse('notifications'))
        self.assertContains(response, 'notification-unread')
        self.assertContains(response, '1 unread')
        self.assertContains(response, reverse('profile', args=[self.actor.username]))
        response = self.client.get(reverse('last_notifications'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, 'answered your question')
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_read)

    def test_count_includes_more_than_five_but_preview_is_limited(self):
        Notification.objects.bulk_create([
            Notification(from_user=self.actor, to_user=self.recipient, question=self.question,
                         notification_type=Notification.FAVORITED) for _ in range(8)
        ])
        Notification.objects.create(from_user=self.actor, to_user=self.outsider,
                                    notification_type=Notification.MENTOR_APPROVED)
        response = self.client.get(reverse('check_notifications'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.content, b'9')
        response = self.client.get(reverse('last_notifications'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(len(response.context['notifications']), 5)
        self.assertEqual(Notification.objects.filter(to_user=self.recipient, is_read=False).count(), 9)

    def test_open_marks_read_and_redirects_to_answer(self):
        target = reverse('question', args=[self.question.pk]) + f'#answer-{self.answer.pk}'
        response = self.client.post(reverse('open_notification', args=[self.notification.pk]))
        self.assertRedirects(response, target)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        self.assertContains(self.client.get(reverse('question', args=[self.question.pk])), f'id="answer-{self.answer.pk}"')

    def test_individual_and_bulk_read_only_affect_current_user(self):
        foreign = Notification.objects.create(from_user=self.actor, to_user=self.outsider,
                                              notification_type=Notification.MENTOR_APPROVED)
        self.assertRedirects(self.client.post(reverse('mark_notification_read', args=[self.notification.pk])), reverse('notifications'))
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        Notification.objects.filter(pk=self.notification.pk).update(is_read=False)
        self.assertRedirects(self.client.post(reverse('mark_all_notifications_read')), reverse('notifications'))
        self.notification.refresh_from_db()
        foreign.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        self.assertFalse(foreign.is_read)

    def test_cannot_open_or_update_someone_elses_notification(self):
        self.client.force_login(self.outsider)
        for route in ['open_notification', 'mark_notification_read']:
            self.assertEqual(self.client.post(reverse(route, args=[self.notification.pk])).status_code, 404)
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_read)
        self.assertNotContains(self.client.get(reverse('notifications')), 'A question')

    def test_read_actions_require_post_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.recipient)
        for route, args in [('open_notification', [self.notification.pk]),
                            ('mark_notification_read', [self.notification.pk]),
                            ('mark_all_notifications_read', [])]:
            url = reverse(route, args=args)
            self.assertEqual(self.client.get(url).status_code, 405)
            self.assertEqual(client.post(url).status_code, 403)
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_read)

    def test_all_notification_endpoints_require_login(self):
        self.client.logout()
        for route in ['notifications', 'last_notifications', 'check_notifications']:
            self.assertEqual(self.client.get(reverse(route)).status_code, 302)
        self.assertEqual(self.client.post(reverse('mark_all_notifications_read')).status_code, 302)

    def test_notification_text_is_escaped(self):
        self.question.title = '<script>alert(1)</script>'
        self.question.save()
        self.actor.first_name = '<img src=x onerror=alert(1)>'
        self.actor.save()
        response = self.client.get(reverse('notifications'))
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertNotContains(response, '<img src=x onerror=alert(1)>')
        self.assertContains(response, '&lt;script&gt;')

    def test_new_answers_include_direct_target_for_all_recipients(self):
        self.client.force_login(self.outsider)
        response = self.client.post(reverse('answer'), {'question': self.question.pk, 'description': 'Another answer'})
        self.assertEqual(response.status_code, 302)
        answer = Answer.objects.latest('pk')
        notifications = Notification.objects.filter(from_user=self.outsider, answer=answer)
        self.assertEqual(set(notifications.values_list('to_user_id', flat=True)), {self.recipient.pk, self.actor.pk})
        for notification in notifications:
            self.assertTrue(notification.get_target_url().endswith(f'#answer-{answer.pk}'))

    def test_legacy_notifications_and_article_links_still_work(self):
        from articles.models import Article
        legacy = Notification.objects.create(from_user=self.actor, to_user=self.recipient,
                                             question=self.question, notification_type=Notification.ANSWERED)
        self.assertEqual(legacy.get_target_url(), reverse('question', args=[self.question.pk]))
        article = Article.objects.create(create_user=self.actor, title='An article', content='Content', status='P')
        notification = Notification.objects.create(from_user=self.actor, to_user=self.recipient,
                                                   article=article, notification_type=Notification.COMMENTED)
        self.assertEqual(notification.get_target_url(), reverse('article', args=[article.slug]))
        self.assertContains(self.client.get(reverse('notifications')), 'commented on your article')
