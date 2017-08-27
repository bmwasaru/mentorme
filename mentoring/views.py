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

    return render(request, 'mentoring/_inbox.html', {
        'messages': messages,
        'conversations': conversations,
        'active': active_conversation
        })


# our view
@login_required
def contact(request):
    form_class = ContactForm

    # new logic!
    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get(
                'contact_name'
            , '')
            contact_email = request.POST.get(
                'contact_email'
            , '')
            form_content = request.POST.get('content', '')

            # Email the profile with the 
            # contact information
            template = get_template('mentoring/contact_template.txt')
            context = Context({
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
            })
            content = template.render(context)

            email = EmailMessage(
                "New contact form submission",
                content,
                "Your website" +'',
                ['youremail@gmail.com'],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            return redirect('contact')

    return render(request, 'mentoring/contact.html', {
        'form': form_class,
    })


@login_required
def mentoring(request):
	if request.user.profile.role=='mentor':
		users_list = User.objects.filter(profile__role='mentee').order_by('username')
		return render(request, 'mentoring/_mentors.html', {'users_list': users_list})
	else:
		users_list = User.objects.filter(profile__role='mentor').order_by('username')
		return render(request, 'mentoring/_mentees.html', {'users_list': users_list})


@login_required
def request_mentorship(request):
	subject = 'Request Mentorship'
	to_user_username = request.POST.get('username')
	# to_user = User.objects.get(id).filter(username=to_user_username)
	print(to_user_username)
	to = [request.user]
	from_email = 'noreply@mentor001.org'
	message = """Hey Lucy, 
	
As you know, I’ve reached a stage in my career where I want to 
[specialise in XXX/ move into management/ take my skills to the next level]. 

Looking forward to hearing from you. 

Cheers,
"""
	email = send_mail(subject=subject, message=message, from_email=from_email, recipient_list=to)
	return render(request, 'mentoring/_email.html', {'email': email})