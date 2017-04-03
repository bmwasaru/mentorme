from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from .choices import ROLE_CHOICES, GENDER_CHOICES


def generate_activation_key(email):
    pass


class UserProfileManager(models.Manager):

    def create(self, user, role):
        profile = UserProfile(user=user, role=role)
        profile.save()
        return profile


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    role = models.CharField(max_length=12, blank=False, choices=ROLE_CHOICES)

    objects = UserProfileManager()

    def get_app(self):
        """Return the user's app in the DB"""
        if self.role == 'mentor':
            return self.mentorapplication
        elif self.role == 'mentee':
            return self.menteeapplication
        else:
            assert False


class UserApplication(models.Model):
    """User Application Base Model
    common fields in both MentorApplication and MenteeApplication"""

    class Meta:
        abstract = True

    APPLICATION_STATUS = (
        ('pending.approval', 'Pending Approval'),
        ('pending.activation', 'Pending Activation'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    )

    user = models.OneToOneField(User, null=True, editable=False)
    profile = models.OneToOneField(UserProfile, null=True, editable=False)
    bio = models.TextField(blank=False)
    gender = models.CharField(
        max_length=6, blank=False, choices=GENDER_CHOICES)
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=32, blank=False)
    last_name = models.CharField(max_length=32, blank=False)
    phone_number = models.CharField(max_length=32, blank=False)
    activation_key = models.CharField(max_length=40,
                                      editable=False,
                                      unique=False)
    timestamp = models.DateTimeField(auto_now=True, editable=False)
    status = models.CharField(max_length=64,
                              editable=False,
                              unique=False,
                              default='pending.approval',
                              choices=APPLICATION_STATUS)

    def approve(self):
        """
        Approves the application. This includes
        (1) Changing status to pending.activation.
        (2) Sending user an activation link
        """
        if self.status == 'pending.approval':
            self.status = 'pending.activation'
            self.activation_key = generate_activation_key(self.email)
        elif self.status == 'pending.activation':
            # resend approval notice
            pass
        else:
            return

        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()

        subject = 'Mentor001 Application Approved'
        text = render_to_string('user/approval_email.html',
                                {'activation_key': self.activation_key,
                                    'first_name': self.first_name,
                                 'last_name': self.last_name,
                                 'site_name': current_site.name,
                                 'domain': current_site.domain})

        from django.core.mail import send_mail
        send_mail(subject, text, 'bmwasaru@gmail.com', [self.email])

        self.save()

    def activate(self, user, profile):
        """
        Activates an application, marking its status active.
        """
        if self.status != 'pending.activation':
            return
        self.status = 'active'
        self.activation_key = ''
        self.user = user            # set user key
        self.profile = profile      # set profile key
        self.save()
        return

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class MenteeApplication(UserApplication):
    """
    Mentee Application Model
    """
    expectations = models.TextField(blank=True,
                                  verbose_name="Tell us about your expectations?")


class MentorApplication(UserApplication):
    """
    Mentor Application Model
    """
    current_occupation = models.CharField(max_length=64,
                                          blank=True,
                                          verbose_name="Current Occupation?")
