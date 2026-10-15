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
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST
from activities.models import Notification
import logging

logger = logging.getLogger(__name__)

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
    if request.user.profile.role == 'mentor':
        accepted = Connection.objects.filter(mentor=request.user.pk, status=Connection.ACCEPTED)
        return render(request, 'mentoring/mentors.html', {
            'users_list': User.objects.filter(pk__in=accepted.values('user')).select_related('profile'),
            'pending_requests': Connection.objects.filter(
                mentor=request.user.pk, status=Connection.PENDING,
            ).select_related('user__profile'),
        })
    condition = Q()
    for area in request.user.profile.mentorship_areas:
        condition |= Q(profile__mentorship_areas__icontains=area)
    users = User.objects.filter(condition, profile__role='mentor', is_active=True).select_related('profile')[:6]
    return render(request, 'mentoring/mentees.html', {'users_list': users})


@login_required
@require_POST
def make_connection(request):
    if request.user.profile.role != 'mentee':
        return HttpResponseForbidden()
    mentor = get_object_or_404(User, username=request.POST.get('to'),
                               profile__role='mentor', is_active=True)
    message = request.POST.get('message', '').strip()
    if not message or mentor.pk == request.user.pk:
        return HttpResponseBadRequest()
    with transaction.atomic():
        # Serialize repeat submissions for this mentee without altering legacy rows.
        User.objects.select_for_update().get(pk=request.user.pk)
        connection = Connection.objects.filter(user=request.user, mentor=mentor.pk).exclude(
            status=Connection.DECLINED,
        ).first()
        created = connection is None
        if created:
            connection = Connection.objects.create(user=request.user, mentor=mentor.pk)
            Message.send_message(request.user, mentor, message)
            Notification.objects.create(from_user=request.user, to_user=mentor,
                                        connection=connection,
                                        notification_type=Notification.MENTORSHIP_REQUESTED)
    if created:
        try:
            send_mail('New mentorship request from MentorMe', message, request.user.email, [mentor.email])
        except Exception:
            logger.warning('Mentorship request email failed for connection %s', connection.pk)
    return redirect('u_profile', username=mentor.username)


@login_required
@require_POST
def respond_connection(request, pk):
    if request.user.profile.role != 'mentor':
        return HttpResponseForbidden()
    status = {'accept': Connection.ACCEPTED, 'decline': Connection.DECLINED}.get(request.POST.get('decision'))
    if status is None:
        return HttpResponseBadRequest()
    with transaction.atomic():
        connection = get_object_or_404(Connection.objects.select_for_update(), pk=pk, mentor=request.user.pk)
        if connection.status == Connection.PENDING:
            connection.status = status
            connection.save(update_fields=['status'])
            Notification.objects.create(
                from_user=request.user, to_user=connection.user, connection=connection,
                notification_type=(Notification.MENTORSHIP_ACCEPTED if status == Connection.ACCEPTED
                                   else Notification.MENTORSHIP_DECLINED),
            )
    return redirect('mentoring')


@login_required
def connections(request):
    if request.user.profile.role == 'mentor':
        ids = Connection.objects.filter(mentor=request.user.pk, status=Connection.ACCEPTED).values('user')
    else:
        ids = Connection.objects.filter(user=request.user, status=Connection.ACCEPTED).values('mentor')
    users = User.objects.filter(pk__in=ids).select_related('profile')
    return render(request, 'mentoring/connections.html', {'connections': users})
