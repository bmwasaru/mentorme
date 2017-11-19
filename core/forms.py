from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from core.choices import EDUCATION_CHOICES, MENTORSHIP_AREAS_CHOICES

from authentication.models import Profile
from authentication.choices import GENDER_CHOICES, ROLE_CHOICES


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=False)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=False)
    location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False)
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False)
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=75,
        required=False)
    gender = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}), 
        choices=GENDER_CHOICES)
    role = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}), 
        choices=ROLE_CHOICES)
    mentorship_areas = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, 
        choices=MENTORSHIP_AREAS_CHOICES)
    highest_level_of_study = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}), 
        choices=EDUCATION_CHOICES)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
        'gender', 'location', 'role', 'mentorship_areas', 'bio',
        'highest_level_of_study', 'profile_picture']
        
        widgets = {
            'bio': forms.Textarea(
                attrs={'cols': 30, 'rows': 10, 'class': 'form-control'}),
        }


class ChangePasswordForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Old password",
        required=True)

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New password",
        required=True)
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm new password",
        required=True)

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'confirm_password']

    def clean(self):
        super(ChangePasswordForm, self).clean()
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        id = self.cleaned_data.get('id')
        user = User.objects.get(pk=id)
        if not user.check_password(old_password):
            self._errors['old_password'] = self.error_class([
                'Old password don\'t match'])
        if new_password and new_password != confirm_password:
            self._errors['new_password'] = self.error_class([
                'Passwords don\'t match'])
        return self.cleaned_data


class contact_form(forms.Form):
    sender = forms.EmailField(max_length = 225, required =True, label = '',
        widget = forms.EmailInput(attrs={'class': 'form-control', 
            'placeholder':'Your Email', 'required':'true'}))
    
    subject = forms.CharField(max_length = 100, required =True, label='',
        widget = forms.TextInput(attrs={'class': 'form-control', 
            'placeholder':'Subject', 'require':'true'}))
    
    message = forms.CharField(widget = forms.Textarea(attrs={
        'class': 'form-control', 
        'rows': 4,
        'placeholder':'Enter your Message', 'required':'true'
        }), 
        required =True, label='')