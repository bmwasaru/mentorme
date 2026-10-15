from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Activity(models.Model):
    FAVORITE = 'F'
    LIKE = 'L'
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (FAVORITE, 'Favorite'),
        (LIKE, 'Like'),
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    question = models.IntegerField(null=True, blank=True)
    answer = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return self.activity_type


class Notification(models.Model):
    FAVORITED = 'F'
    ANSWERED = 'A'
    ACCEPTED_ANSWER = 'W'
    ALSO_ANSWERED = 'S'
    EDITED_ARTICLE = 'E'
    ALSO_COMMENTED = 'D'
    COMMENTED = 'C'
    MENTORSHIP_REQUESTED = 'M'
    MENTORSHIP_ACCEPTED = 'Y'
    MENTORSHIP_DECLINED = 'N'
    MENTOR_APPROVED = 'V'
    NOTIFICATION_TYPES = (
        (FAVORITED, 'Favorited'),
        (ANSWERED, 'Answered'),
        (ACCEPTED_ANSWER, 'Accepted Answer'),
        (EDITED_ARTICLE, 'Edited Article'),
        (COMMENTED, 'Commented'),
        (ALSO_COMMENTED, 'Also Commented'),
        (ALSO_ANSWERED, 'Also Answered'),
        (MENTORSHIP_REQUESTED, 'Mentorship Requested'),
        (MENTORSHIP_ACCEPTED, 'Mentorship Accepted'),
        (MENTORSHIP_DECLINED, 'Mentorship Declined'),
        (MENTOR_APPROVED, 'Mentor Approved'),
    )

    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    date = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey('questions.Question', on_delete=models.PROTECT, null=True, blank=True)
    answer = models.ForeignKey('questions.Answer', on_delete=models.PROTECT, null=True, blank=True)
    article = models.ForeignKey('articles.Article', on_delete=models.PROTECT, null=True, blank=True)
    connection = models.ForeignKey('authentication.Connection', on_delete=models.SET_NULL, null=True, blank=True)
    notification_type = models.CharField(max_length=1,
                                         choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ('-date', '-pk')
        indexes = [models.Index(fields=['to_user', 'is_read', '-date'], name='notification_unread_idx')]

    def get_target_url(self):
        if self.answer_id:
            return reverse('question', args=[self.answer.question_id]) + f'#answer-{self.answer_id}'
        if self.question_id:
            return reverse('question', args=[self.question_id])
        if self.article_id:
            return reverse('article', args=[self.article.slug])
        if self.notification_type == self.MENTORSHIP_ACCEPTED:
            return reverse('connections')
        if self.notification_type in {self.MENTORSHIP_REQUESTED,
                                      self.MENTORSHIP_DECLINED, self.MENTOR_APPROVED}:
            return reverse('mentoring')
        return reverse('notifications')

    def get_message(self):
        title = self.question.title if self.question_id else ''
        article = self.article.title if self.article_id else ''
        messages = {
            self.FAVORITED: f'favorited your question: {title}',
            self.ANSWERED: f'answered your question: {title}',
            self.ACCEPTED_ANSWER: 'accepted your answer',
            self.ALSO_ANSWERED: f'also answered: {title}',
            self.COMMENTED: f'commented on your article: {article}',
            self.ALSO_COMMENTED: f'also commented on: {article}',
            self.EDITED_ARTICLE: f'edited an article: {article}',
            self.MENTORSHIP_REQUESTED: 'requested mentorship from you',
            self.MENTORSHIP_ACCEPTED: 'accepted your mentorship request',
            self.MENTORSHIP_DECLINED: 'declined your mentorship request',
            self.MENTOR_APPROVED: 'approved your mentor account. You can now use the platform.',
        }
        return messages.get(self.notification_type, 'sent you a notification')

    def __str__(self):
        return f'{self.from_user.profile.get_screen_name()} {self.get_message()}'
