from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse


class InitialsAvatarTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='brian_mwachofi', first_name='Brian', last_name='Mwachofi',
        )
        self.client.force_login(self.user)

    def test_initials_use_names_and_fall_back_to_username(self):
        cases = [
            ('Brian', 'Mwachofi', 'member', 'BM'),
            (' Brian Mark ', ' Mwachofi ', 'member', 'BM'),
            ('Brian', '', 'member', 'B'),
            ('', 'Mwachofi', 'member', 'M'),
            ('Élodie', 'Durand', 'member', 'ÉD'),
            ('', '', 'brian_mwachofi', 'BM'),
            ('', '', 'brian', 'BR'),
        ]
        for first, last, username, expected in cases:
            with self.subTest(first=first, last=last, username=username):
                self.user.first_name, self.user.last_name, self.user.username = first, last, username
                self.assertEqual(self.user.profile.get_initials(), expected)

    def test_profiles_render_initials_instead_of_legacy_upload(self):
        self.user.profile.profile_picture.name = 'profiles/legacy.jpg'
        self.user.profile.save()
        for url in [reverse('profile', args=[self.user.username]),
                    reverse('u_profile', args=[self.user.username]), reverse('mentees')]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'aria-label="Brian Mwachofi"')
                self.assertContains(response, '<span aria-hidden="true">BM</span>', html=True)
                self.assertNotContains(response, 'profiles/legacy.jpg')

    def test_setup_and_settings_have_no_upload_controls(self):
        for route in ['initial_setup', 'settings']:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertNotContains(response, 'type="file"')
                self.assertNotContains(response, 'multipart/form-data')
                self.assertNotIn('profile_picture', response.context['form'].fields)

    def test_changing_name_updates_initials_and_ignores_uploaded_file(self):
        self.user.profile.profile_picture.name = 'profiles/legacy.jpg'
        self.user.profile.save()
        response = self.client.post(reverse('settings'), {
            'first_name': 'Alice', 'last_name': 'Kamau', 'gender': 'Female',
            'bio': 'Learning technology', 'mentorship_areas': ['technology'],
            'highest_level_of_study': 'undergraduate',
            'profile_picture': SimpleUploadedFile('new.jpg', b'not-an-image', content_type='image/jpeg'),
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.profile_picture.name, 'profiles/legacy.jpg')
        self.assertEqual(self.user.profile.get_initials(), 'AK')
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertContains(response, '<span aria-hidden="true">AK</span>', html=True)
        self.assertNotContains(response, 'new.jpg')
