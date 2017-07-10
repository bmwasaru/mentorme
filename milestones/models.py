from django.contrib.auth.models import User
from django.db import models
import markdown

from authentication.models import Profile


class Milestone(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField(max_length=255)
	description = models.TextField()
	create_date = models.DateTimeField(auto_now_add=True)
	start_date = models.DateField()
	due_date = models.DateField()
	# mentee = models.ForeignKey(User)
	has_completed_milestone = models.BooleanField(default=False)

	class Meta:
		verbose_name = 'milestone'
		verbose_name_plural = 'milestones'
		ordering = ('-create_date',)

	def __str__(self):
		return self.title

	@staticmethod
	def get_completed():
		return Milestone.objects.filter(has_completed_milestone=True)

	@staticmethod
	def get_pending():
		return Milestone.objects.filter(has_completed_milestone=False)

	def get_milestones_count(self):
		return Milestone.objects.filter(mentee=request.user)

	def get_remaining_days(self):
		return self.due_date - self.start_date


class Comment(models.Model):
    user = models.ForeignKey(User)
    milestone = models.ForeignKey(Milestone)
    description = models.TextField(max_length=2000)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('create_date',)

    def __str__(self):
        return self.description

    def get_description_as_markdown(self):
        return markdown.markdown(self.description, safe_mode='escape')

    def get_cooments(self):
        return Comment.objects.filter(milestone=self).order_by('-create_date')

    # def accept(self):
    #     answers = Answer.objects.filter(question=self.question)
    #     for answer in answers:
    #         answer.is_accepted = False
    #         answer.save()
    #     self.is_accepted = True
    #     self.save()
    #     self.question.has_accepted_answer = True
    #     self.question.save()