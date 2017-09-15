from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect

# from core.forms import ProfileForm, EducationForm, ExperienceForm, MentorshipAreaForm
# from authentication.models import Profile
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.template import Context
from django.template.loader import get_template

from mentoring.forms import ContactForm
from messenger.models import Message

from articles.decorators import user_is_mentor

from django.db.models import Q

@login_required
def u_profile(request, username):
    page_user = get_object_or_404(User, username=username)
    return render(request, 'mentoring/_profile.html', {
        'page_user': page_user
        })


@login_required
def u_education(request):
    users = Education.objects.filter(user=request.user)
    return redirect(request, 'mentoring/_education.html', {'users': users})


@login_required
def u_inbox(request):
    conversations = Message.get_conversations(user=request.user)
    active_conversation = None
    messages = None
    if conversations:
        conversation = conversations[0]
        active_conversation = conversation['user'].username
        messages = Message.objects.filter(user=request.user,
                                          conversation=conversation['user'])
        messages.update(is_read=True)
        for conversation in conversations:
            if conversation['user'].username == active_conversation:
                conversation['unread'] = 0

    return render(request, 'mentor001/profile.html', {
        'messages': messages,
        'conversations': conversations,
        'active': active_conversation
        })


@login_required
def u_messages(request, username):
    conversations = Message.get_conversations(user=request.user)
    active_conversation = username
    messages = Message.objects.filter(user=request.user,
                                      conversation__username=username)
    messages.update(is_read=True)
    for conversation in conversations:
        if conversation['user'].username == username:
            conversation['unread'] = 0

    return render(request, 'mentoring/_profile.html', {
        'messages': messages,
        'conversations': conversations,
        'active': active_conversation
        })


@login_required
def mentoring(request):
    strings = list(request.user.profile.mentorship_areas)
    condition = Q(profile__mentorship_areas__icontains=strings[0])
    for string in strings[1:]:
            condition |= Q(profile__mentorship_areas__icontains=string)

    if request.user.profile.role=='mentor':
        users_list = User.objects.filter(condition,
            profile__role='mentor').order_by('username')[:6]
        return render(request, 
            'mentoring/_mentors.html', 
            {'users_list': users_list})
    else:
        users_list = User.objects.filter(condition, 
            profile__role='mentor')[:6]
        return render(request, 'mentoring/_mentees.html', 
            {'users_list': users_list})


@login_required
def request_mentorship(request):
    if request.method == 'POST':
        from_user = request.user
        to_user_username = request.POST.get('to')
        try:
            to_user = User.objects.get(username=to_user_username)

        except Exception:
            try:
                to_user_username = to_user_username[
                    to_user_username.rfind('(')+1:len(to_user_username)-1]
                to_user = User.objects.get(username=to_user_username)

            except Exception:
                return redirect('/mentoring/request_mentorship/')

        message = request.POST.get('message')
        if len(message.strip()) == 0:
            return redirect('/mentoring/request_mentorship/')

        if from_user != to_user:
            Message.send_message(from_user, to_user, message)

        return redirect('/mentoring/{0}/'.format(to_user_username))

    else:
        conversations = Message.get_conversations(user=request.user)
        return render(request, 'mentoring/_profile.html',
                      {'conversations': conversations})


