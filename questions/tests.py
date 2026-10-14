from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from activities.models import Activity, Notification
from questions.models import Answer, Question, Tag


class QuestionOwnerActionsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='question_owner')
        self.other = User.objects.create_user(username='other_member')
        self.question = Question.objects.create(
            user=self.owner, title='Original question', description='Original description',
            category='technology',
        )
        self.question.create_tags('original learning')
        self.answer = Answer.objects.create(
            question=self.question, user=self.other, description='An existing answer',
        )
        self.favorite = Activity.objects.create(
            user=self.other, question=self.question.pk, activity_type=Activity.FAVORITE,
        )
        self.vote = Activity.objects.create(
            user=self.owner, answer=self.answer.pk, activity_type=Activity.UP_VOTE,
        )
        self.notification = Notification.objects.create(
            from_user=self.other, to_user=self.owner, question=self.question,
            notification_type=Notification.ANSWERED,
        )
        self.accepted_notification = Notification.objects.create(
            from_user=self.owner, to_user=self.other, answer=self.answer,
            notification_type=Notification.ACCEPTED_ANSWER,
        )
        self.edit_url = reverse('edit_question', args=[self.question.pk])
        self.delete_url = reverse('delete_question', args=[self.question.pk])
        self.detail_url = reverse('question', args=[self.question.pk])
        self.data = {'title': 'Updated question', 'description': 'Updated description',
                     'category': 'career_readiness', 'tags': 'career   planning career'}
        self.client.force_login(self.owner)

    def test_owner_sees_controls_and_prefilled_edit_form(self):
        for url in [self.detail_url, reverse('all')]:
            response = self.client.get(url)
            self.assertContains(response, self.edit_url)
            self.assertContains(response, self.delete_url)
        response = self.client.get(self.edit_url)
        self.assertContains(response, 'Original question')
        self.assertEqual(response.context['form']['description'].value(), 'Original description')
        self.assertEqual(set(response.context['form']['tags'].value().split()), {'original', 'learning'})

    def test_edit_preserves_owner_answers_and_activity(self):
        old_date = timezone.now() - timedelta(days=1)
        Question.objects.filter(pk=self.question.pk).update(update_date=old_date)
        self.client.get(reverse('all'))
        response = self.client.post(self.edit_url, {**self.data, 'user': self.other.pk, 'favorites': 100})
        self.assertRedirects(response, self.detail_url)
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, 'Updated question')
        self.assertEqual(self.question.description, 'Updated description')
        self.assertEqual(self.question.category, 'career_readiness')
        self.assertEqual(self.question.user, self.owner)
        self.assertEqual(self.question.favorites, 0)
        self.assertGreater(self.question.update_date, old_date)
        self.assertEqual(set(self.question.get_tags().values_list('tag', flat=True)), {'career', 'planning'})
        self.assertEqual(self.question.get_tags().count(), 2)
        self.assertTrue(Answer.objects.filter(pk=self.answer.pk).exists())
        self.assertTrue(Activity.objects.filter(pk=self.favorite.pk).exists())
        self.assertTrue(Notification.objects.filter(pk=self.notification.pk).exists())
        self.assertContains(self.client.get(reverse('all')), 'Updated question')

    def test_edit_can_clear_tags(self):
        self.assertRedirects(self.client.post(self.edit_url, {**self.data, 'tags': ''}), self.detail_url)
        self.assertFalse(self.question.get_tags().exists())

    def test_invalid_edit_does_not_change_question_or_tags(self):
        response = self.client.post(self.edit_url, {**self.data, 'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, 'Original question')
        self.assertEqual(set(self.question.get_tags().values_list('tag', flat=True)), {'original', 'learning'})

    def test_other_member_cannot_edit_or_delete(self):
        self.client.force_login(self.other)
        for url in [self.detail_url, reverse('all')]:
            response = self.client.get(url)
            self.assertNotContains(response, self.edit_url)
            self.assertNotContains(response, self.delete_url)
        for url in [self.edit_url, self.delete_url]:
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, self.data).status_code, 403)
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, 'Original question')
        self.assertTrue(Answer.objects.filter(pk=self.answer.pk).exists())

    def test_anonymous_requests_require_login(self):
        self.client.logout()
        for url in [self.edit_url, self.delete_url]:
            for method in [self.client.get, self.client.post]:
                self.assertRedirects(method(url), '/?next=' + url, fetch_redirect_response=False)

    def test_delete_confirmation_does_not_delete(self):
        response = self.client.get(self.delete_url)
        self.assertContains(response, 'Its answers will also be deleted.')
        self.assertContains(response, 'Original question')
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())
        self.assertTrue(Answer.objects.filter(pk=self.answer.pk).exists())

    def test_delete_removes_thread_and_related_records_only(self):
        unrelated = Question.objects.create(user=self.other, title='Keep this question', category='technology')
        unrelated.create_tags('keep')
        unrelated_answer = Answer.objects.create(user=self.owner, question=unrelated, description='Keep this answer')
        unrelated_activity = Activity.objects.create(user=self.owner, question=unrelated.pk, activity_type=Activity.FAVORITE)
        unrelated_notification = Notification.objects.create(
            from_user=self.owner, to_user=self.other, question=unrelated, notification_type=Notification.FAVORITED,
        )
        self.client.get(reverse('all'))
        self.assertRedirects(self.client.post(self.delete_url), reverse('questions'))
        self.assertFalse(Question.objects.filter(pk=self.question.pk).exists())
        self.assertFalse(Answer.objects.filter(pk=self.answer.pk).exists())
        self.assertFalse(Tag.objects.filter(question_id=self.question.pk).exists())
        self.assertFalse(Activity.objects.filter(pk__in=[self.favorite.pk, self.vote.pk]).exists())
        self.assertFalse(Notification.objects.filter(pk__in=[self.notification.pk, self.accepted_notification.pk]).exists())
        self.assertTrue(Question.objects.filter(pk=unrelated.pk).exists())
        self.assertTrue(Answer.objects.filter(pk=unrelated_answer.pk).exists())
        self.assertTrue(Activity.objects.filter(pk=unrelated_activity.pk).exists())
        self.assertTrue(Notification.objects.filter(pk=unrelated_notification.pk).exists())
        self.assertTrue(unrelated.get_tags().exists())
        self.assertEqual(User.objects.count(), 2)
        self.assertNotContains(self.client.get(reverse('all')), 'Original question')
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_mutations_require_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        client.get(self.delete_url)
        self.assertEqual(client.post(self.edit_url, self.data).status_code, 403)
        self.assertEqual(client.post(self.delete_url).status_code, 403)
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())
        response = client.post(self.delete_url, {'csrfmiddlewaretoken': client.cookies['csrftoken'].value})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Question.objects.filter(pk=self.question.pk).exists())

    def test_missing_questions_return_404(self):
        for route in ['edit_question', 'delete_question']:
            url = reverse(route, args=[999999])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, self.data).status_code, 404)
