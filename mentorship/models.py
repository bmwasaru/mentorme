from django.db import models
from django.contrib.auth.models import User


class Mentorship(models.Model):
    mentor = models.ForeignKey(User, related_name='mentorship_mentor')
    mentee = models.ForeignKey(User, related_name='mentorship_mentee')
    accepted = models.BooleanField(default=False)
    date_started = models.DateTimeField(auto_now=True)
    date_ended = models.DateTimeField()

    def __str__(self):
        return "mentor {0} - mentee {1}".format(self.mentor, self.mentee)
