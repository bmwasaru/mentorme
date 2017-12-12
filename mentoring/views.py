from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.template import Context
from django.template.loader import get_template
from django.db.models import Q

from mentoring.forms import ContactForm
from messenger.models import Message
from authentication.models import Connection
from articles.decorators import user_is_mentor


@login_required
def u_profile(request, username):
    page_user = get_object_or_404(User, username=username)
    return render(request, 'mentoring/profile.html', {
        'page_user': page_user
        })


@login_required
def u_education(request):
    users = Education.objects.filter(user=request.user)
    return redirect(request, 'mentoring/education.html', {'users': users})


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

    return render(request, 'mentoring/profile.html', {
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

    return render(request, 'mentoring/profile.html', {
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
        connections = list(Connection.objects.values_list(
            'user', flat=True).filter(mentor=request.user.id).distinct())
        if connections:
            users_list = User.objects.filter(pk__in=connections)
            return render(request, 
                        'mentoring/mentors.html', 
                        {'users_list': users_list})
        else:
            users_list = messages.add_message(request, messages.SUCCESS, 
                'Sorry we do not have mentees for you.')
            return render(request, 'mentoring/mentors.html', {'users_list': users_list})
    else:
        users_list = User.objects.filter(condition, 
            profile__role='mentor')[:6]
        return render(request, 'mentoring/mentees.html', 
            {'users_list': users_list})


@login_required
def make_connection(request):
    user = request.user
    mentor = request.POST.get('to', None)
    mentor_object = User.objects.get(username=mentor)
    mentor_id = mentor_object.id

    subject = "Possible mentee connection from Mentor001"
    message = request.POST.get('message')
    sender = request.user.email
    
    if user != mentor_object:
        Message.send_message(user, mentor_object, message)
            
    recipient = [mentor_object.email]
    try:
        if user.profile.role == 'mentor':
            new_connection = Connection(user=user, mentor=mentor_id, status=1)
            new_connection.save()
        else:
            new_connection = Connection(user=user, mentor=mentor_id)
            new_connection.save()
        send_mail(subject, message, sender, recipient)
    except Exception:
        return HttpResponse('invalid header found')

    data = {
        'confirm': 'Connection complete',
    }

    return redirect('/mentoring/{0}/'.format(mentor))


@login_required
def connections(request):
    user = request.user
    if user.profile.role == 'mentor':
        con = list(Connection.objects.values_list('mentor', flat=True).filter(
            user=user.id, status=1))
        connections = User.objects.filter(pk__in=con)
        return render(request, 'mentoring/connections.html', 
            {'connections': connections})
    else:
        con = list(Connection.objects.values_list('user', flat=True).filter(
            mentor=user.id, status=1))
        connections = User.objects.filter(pk__in=con)
        return render(request, 'mentoring/connections.html', 
            {'connections': connections})  