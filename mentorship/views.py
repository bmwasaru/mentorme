from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Mentorship


@login_required
def request_mentorship(request, mentor_id):
    user = request.user
    # Check if mentee is already in mentorship
    if Mentorship.objects.filter(mentee=request.user).count() > 0:
        messages.add_message(request,
                             messages.ERROR,
                             'You already have a mentor.')
    # Check if mentor already has a three mentees
    if Mentorship.objects.filter(mentor=mentor_id).count() == 3:
        messages.add_message(request,
                             messages.ERROR,
                             'Sorry, this mentor has enough mentees.')
    Mentorship.objects.create(mentee=user, mentor=mentor_id, accepted=False)
    messages.add_message(request,
                         messages.SUCCESS,
                         'Your mentorship request has been sent.')



