from django import forms

from questions.models import Answer, Question
from core.choices import MENTORSHIP_AREAS_CHOICES


class QuestionForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255)
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        max_length=2000)
    tags = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255,
        required=False,
        help_text='Use spaces to separate the tags')  # noqa: E501
    category = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices = MENTORSHIP_AREAS_CHOICES, 
        label="", 
        initial='', 
        required=True)

    class Meta:
        model = Question
        fields = ['title', 'description', 'tags', 'category']


class AnswerForm(forms.ModelForm):
    question = forms.ModelChoiceField(widget=forms.HiddenInput(),
                                      queryset=Question.objects.all())
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        max_length=2000)

    class Meta:
        model = Answer
        fields = ['question', 'description']
