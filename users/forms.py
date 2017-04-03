from django import forms

from users.models import MenteeApplication, MentorApplication


class ApplicationForm(forms.ModelForm):

    def save(self, *args, **kwargs):
        app = super(ApplicationForm, self).save(*args, **kwargs)

        if app.user is None:
            app.save()
            return app

        # update redundant information
        app.user.first_name = app.first_name
        app.user.last_name = app.last_name
        app.user.save()

        return app


class MentorApplicationForm(ApplicationForm):
    role = 'mentor'

    class Meta:
        model = MentorApplication
        fields = ('email',
                  'first_name',
                  'last_name',
                  'bio',
                  'gender',
                  'phone_number',
                  'current_occupation')


class MenteeApplicationForm(ApplicationForm):
    role = 'mentee'

    class Meta:
        model = MenteeApplication
        fields = ('email',
                  'first_name',
                  'last_name',
                  'bio',
                  'gender',
                  'phone_number',
                  'expectations')
