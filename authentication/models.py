from __future__ import unicode_literals

import hashlib
import urllib
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible

from .choices import GENDER_CHOICES, ROLE_CHOICES


@python_2_unicode_compatible
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(blank=True, default='')
    gender = models.CharField(
        max_length=6, blank=True, choices=GENDER_CHOICES)
    role = models.CharField(max_length=6, blank=False, default='mentee', choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=32, blank=True)

    def is_mentor(self):
        return self.role == 'mentor'

    def is_mentee(self):
        return self.role == 'mentee'

    class Meta:
        db_table = 'auth_profile'

    def __str__(self):
        return self.user.username

    def get_gravatar(self):
        gravatar_url = 'http://www.gravatar.com/avatar/{0}?{1}'.format(
            hashlib.md5(self.user.email.lower().encode('utf-8')).hexdigest(),
            urlencode({'s': '256'})
        )
        return gravatar_url

    def create_interests(self, interest):
        interest = interest.strip()
        interests_list = interest.split(',')
        for interest in interests_list:
            e, created = Interest.objects.get_or_create(interest=interest.lower(), profile=self)

    def get_interests(self):
        return Interest.objects.filter(profile=self)

    def get_screen_name(self):
        try:
            if self.user.get_full_name():
                return self.user.get_full_name()
            else:
                return self.user.username
        except:
            return self.user.username


class Interest(models.Model):
    interest = models.CharField(max_length=255)
    profile = models.ForeignKey(Profile)

    def __str__(self):
        return self.interest

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'
        unique_together = ('interest', 'profile')
        index_together = ['interest', 'profile']


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
