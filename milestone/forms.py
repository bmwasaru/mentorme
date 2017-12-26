from django import forms
from .models import Milestone


class MilestoneForm(forms.ModelForm):
    milestone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=150,
        required=True)

    class Meta:
        model = Milestone
        fields = ['milestone']