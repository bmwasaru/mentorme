from django import forms
from django.contrib.admin import widgets 
from milestones.models import Milestone, Comment


class MilestoneForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255)
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        max_length=2000)
    # start_date = forms.DateTimeField(attrs={'class': 'form-control'})
    # due_date = forms.DateTimeField(attrs={'class': 'form-control'})

    class Meta:
        model = Milestone
        fields = ['title', 'description', 'start_date','due_date']

    def __init__(self, *args, **kwargs):
        super(MilestoneForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget = widgets.AdminDateWidget()
        self.fields['due_date'].widget = widgets.AdminDateWidget()


class CommentForm(forms.ModelForm):
    milestone = forms.ModelChoiceField(widget=forms.HiddenInput(),
                                      queryset=Milestone.objects.all())
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        max_length=2000)

    class Meta:
        model = Comment
        fields = ['milestone', 'description']