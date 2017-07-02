from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Interest(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=255, unique=True)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _('interest')
		verbose_name_plural = _('interests')
		ordering = ('date',)
		db_table = 'interestes'

	def __str__(self):
		return self.name