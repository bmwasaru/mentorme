import hashlib
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from .choices import GENDER_CHOICES, ROLE_CHOICES
from activities.models import Notification


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(blank=True, default='')
    gender = models.CharField(
        max_length=6, blank=True, choices=GENDER_CHOICES)
    role = models.CharField(max_length=6, blank=False,
                            default='mentee', choices=ROLE_CHOICES)
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
        gravatar_url = 'https://www.gravatar.com/avatar/{0}?{1}'.format(
            hashlib.md5(self.user.email.lower().encode('utf-8')).hexdigest(),
            urlencode({'s': '256'})
        )
        return gravatar_url

    def create_interests(self, interest):
        interest = interest.strip()
        interests_list = interest.split(',')
        for interest in interests_list:
            e, created = Interest.objects.get_or_create(
                interest=interest.lower(), profile=self)

    def get_interests(self):
        return Interest.objects.filter(profile=self)

    def get_screen_name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.username

    def notify_favorited(self, question):
        if self.user != question.user:
            Notification(notification_type=Notification.FAVORITED,
                         from_user=self.user, to_user=question.user,
                         question=question).save()

    def unotify_favorited(self, question):
        if self.user != question.user:
            Notification.objects.filter(
                notification_type=Notification.FAVORITED,
                from_user=self.user,
                to_user=question.user,
                question=question).delete()

    def notify_answered(self, question):
        if self.user != question.user:
            Notification(notification_type=Notification.ANSWERED,
                         from_user=self.user,
                         to_user=question.user,
                         question=question).save()

    def notify_also_answered(self, question):
        answers = question.get_answers()
        users = []
        for answer in answers:
            if answer.user != self.user and answer.user != question.user:
                users.append(answer.user.pk)
        users = list(set(users))
        for user in users:
            Notification(notification_type=Notification.ALSO_ANSWERED,
                         from_user=self.user, to_user=User(id=user),
                         question=question).save()

    def notify_accepted(self, answer):
        if self.user != answer.user:
            Notification(notification_type=Notification.ACCEPTED_ANSWER,
                         from_user=self.user,
                         to_user=answer.user,
                         answer=answer).save()

    def unotify_accepted(self, answer):
        if self.user != answer.user:
            Notification.objects.filter(
                notification_type=Notification.ACCEPTED_ANSWER,
                from_user=self.user,
                to_user=answer.user,
                answer=answer).delete()


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


class MentorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=255)


class MenteeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expectations = models.TextField()
