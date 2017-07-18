from django.db import models
from django.contrib.auth.models import User

from multiselectfield import MultiSelectField

from core.choices import EDUCATION_CHOICES, MENTORSHIP_AREAS_CHOICES


class Education(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	level_of_study = models.CharField(max_length=255, choices=EDUCATION_CHOICES)
	institution_name = models.CharField(max_length=255)
	field_of_study = models.CharField(max_length=255)

	def __str__(self):
		return self.education_level

	class Meta:
		verbose_name = 'Education_background'
		verbose_name_plural = 'Education_background'


class Experience(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	employer = models.CharField(max_length=255)
	industry = models.CharField(max_length=255)
	job_title = models.CharField(max_length=255)
	job_description = models.TextField()

	def __str__(self):
		return self.job_title

	class Meta:
		verbose_name = 'Experience'
		verbose_name_plural = 'Experiences'


class MentorshipArea(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	mentorship_areas = MultiSelectField(choices=MENTORSHIP_AREAS_CHOICES, 
        max_choices=3,
        default='')

	def __str__(self):
		return self.mentorship_areas

	class Meta:
		verbose_name = 'Mentorship Area'
		verbose_name_plural = 'Mentorship Areas'