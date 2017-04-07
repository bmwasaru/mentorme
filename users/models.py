from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .choices import GENDER_CHOICES


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, default='')
    gender = models.CharField(
        max_length=6, blank=True, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=32, blank=True)
    expectations = models.TextField(blank=True,
                                    verbose_name="Tell us about your expectations?")
    current_occupation = models.CharField(max_length=64,
                                          blank=True,
                                          verbose_name="Current Occupation?")


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
