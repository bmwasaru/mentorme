from django import forms

from .models import Interest


class InterestForm(forms.ModelForm):
	name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255)

	class Meta:
		model = Interest
		fields = ['name',]