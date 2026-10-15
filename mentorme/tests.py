from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.template import engines
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from activities.models import Notification
from authentication.models import Connection
from mentorme.markdown import render_markdown
from messenger.models import Message
from questions.models import Answer, Question


class UpgradeCompatibilityTests(TestCase):
    def setUp(self):
        self.mentee = User.objects.create_user(username='mentee', email='mentee@example.com')
        self.mentor = User.objects.create_user(username='mentor', email='mentor@example.com')
        self.mentor.profile.role = 'mentor'
        self.mentor.profile.mentorship_areas = ['technology']
        self.mentor.profile.save()
        self.mentee.profile.mentorship_areas = ['technology']
        self.mentee.profile.save()
        self.client.force_login(self.mentee)

    def test_forum_answer_and_notifications(self):
        response = self.client.post(reverse('ask'), {
            'title': 'How do I start?', 'description': '**Please advise**',
            'category': 'technology', 'tags': 'career learning',
        })
        self.assertRedirects(response, reverse('questions'))
        question = Question.objects.get()
        self.client.force_login(self.mentor)
        response = self.client.post(reverse('answer'), {
            'question': question.pk, 'description': 'Start with a small project.',
        })
        self.assertRedirects(response, reverse('question', args=[question.pk]))
        answer = Answer.objects.get()
        self.assertTrue(Notification.objects.filter(
            to_user=self.mentee, notification_type=Notification.ANSWERED,
        ).exists())
        self.client.force_login(self.mentee)
        response = self.client.post(reverse('accept'), {'answer': answer.pk},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        answer.refresh_from_db()
        self.assertTrue(answer.is_accepted)
        self.assertEqual(self.client.get(reverse('notifications')).status_code, 200)
        self.assertTrue(Notification.objects.filter(to_user=self.mentee, is_read=False).exists())

    def test_ajax_messaging(self):
        response = self.client.post(reverse('send_message'), {
            'to': self.mentor.username, 'message': 'Hello!',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.filter(message='Hello!').count(), 2)
        self.assertEqual(self.client.get(reverse('inbox')).status_code, 200)
        self.assertEqual(self.client.get(reverse('check_message')).status_code, 400)

    @patch('mentoring.views.send_mail')
    def test_mentorship_request(self, send_mail):
        self.assertEqual(self.client.get(reverse('mentoring')).status_code, 200)
        response = self.client.post(reverse('make_connection'), {
            'to': self.mentor.username, 'message': 'Please mentor me.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Connection.objects.filter(user=self.mentee, mentor=self.mentor.pk).exists())
        send_mail.assert_called_once()

    def test_milestone_api(self):
        response = self.client.post('/api/milestone/', {'milestone': 'Finish first project'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['user'], self.mentee.username)
        self.assertEqual(self.client.get('/api/milestone/').status_code, 200)

    def test_mentee_cannot_write_articles(self):
        self.assertEqual(self.client.get(reverse('write')).status_code, 403)
        self.assertEqual(self.client.post(reverse('preview'), {'content': 'Hello'},
                                         HTTP_X_REQUESTED_WITH='XMLHttpRequest').status_code, 403)

    def test_markdown_escapes_html_and_removes_unsafe_links(self):
        html = render_markdown('<script>alert(1)</script>\n\n[click](javascript:alert(1))')
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('href="javascript:', html)
        self.assertIn('<strong>text</strong>', render_markdown('**text**'))
        self.assertIn('<blockquote>', render_markdown('> quote'))

    def test_all_project_templates_compile(self):
        root = Path(__file__).resolve().parent.parent
        for directory in root.glob('*/templates'):
            for template in directory.rglob('*.html'):
                with self.subTest(template=str(template.relative_to(root))):
                    engines['django'].from_string(template.read_text())

    def test_pages_with_production_static_storage(self):
        with TemporaryDirectory(prefix='mentorme-static-') as static_root:
            with self.settings(STATIC_ROOT=static_root, STORAGES={
                'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
                'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
            }):
                call_command('collectstatic', interactive=False, verbosity=0)
                for url in ['/account/login/', '/articles/', '/questions/',
                            '/mentoring/', '/messages/', '/notifications/',
                            '/settings/', '/milestone/', '/mentors/', '/mentees/']:
                    with self.subTest(url=url):
                        self.assertEqual(self.client.get(url).status_code, 200)


class ExistingDatabaseUpgradeTests(TransactionTestCase):
    def test_upgrade_preserves_members_and_content(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        previous = [
            ('activities', '0002_auto_20170825_1252'),
            ('articles', '0001_initial'),
            ('authentication', '0026_auto_20171226_0802'),
            ('mentoring', '0002_auto_20170829_2251'),
            ('messenger', '0001_initial'),
            ('questions', '0003_auto_20171129_0808'),
        ]
        executor.migrate(previous)
        try:
            apps = executor.loader.project_state(previous).apps
            user = apps.get_model('auth', 'User').objects.create(username='existing_member')
            apps.get_model('authentication', 'Profile').objects.create(user_id=user.pk)
            question = apps.get_model('questions', 'Question').objects.create(
                user_id=user.pk, title='Existing question', description='Existing content',
            )
            apps.get_model('questions', 'Tag').objects.create(question_id=question.pk, tag='career')
            apps.get_model('articles', 'Article').objects.create(
                create_user_id=user.pk, title='Existing article', content='Existing content', status='P',
            )
        finally:
            MigrationExecutor(connection).migrate(latest)
        self.assertTrue(User.objects.filter(username='existing_member').exists())
        self.assertTrue(Question.objects.filter(title='Existing question').exists())
        from articles.models import Article
        from questions.models import Tag
        self.assertEqual(Article.objects.get(title='Existing article').create_user.username, 'existing_member')
        self.assertEqual(Tag.objects.get(tag='career').question.title, 'Existing question')
