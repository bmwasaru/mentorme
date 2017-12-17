from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone


class Milestone(models.Model):
    user = models.ForeignKey(
        User, null=True, related_name='milestone', on_delete=models.CASCADE)
    milestone = models.CharField(max_length=128, default='')
    created_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True)
    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.milestone

    def count(self):
        return self.milestone.count()

    def count_finished(self):
        return self.milestone.fiter(is_finished=True).count()

    def count_open(self):
        return self.milestone.fiter(is_finished=False).count()

    def close(self):
        self.is_finished = True
        self.finished_at = timezone.now()
        self.save()

    def reopen(self):
        self.is_finished = False
        self.finished_at = None
        self.save()