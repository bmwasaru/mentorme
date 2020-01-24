from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = (
    ('accepted', 'accepted'),
    ('declined', 'declined'),
    ('completed', 'completed'),)


class Mentorship(models.Model):
    mentor = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT)
    mentee = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return self.status
