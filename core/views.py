from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError

from .forms import (ChangePasswordForm, ProfileForm, ContactForm, InterestForm)
from authentication.models import Profile, Connection
import os
from PIL import Image


def image_resize(image):
    size_300=(300,300)
    img = Image.open(image)
    fn, fext = os.path.splitext(image)
    img.thumbnail(size_300)
    img.save('media/profiles/{}_300{}'.format(fn, fext))


def index(request):
    return render(request, 'core/includes/cover.html')


def home(request):
    if request.user.is_authenticated():
        # TODO: return milestones
        return HttpResponseRedirect('/questions/')
    else:
        form = ContactForm
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message'] 
                sender = form.cleaned_data['sender']

            recipient = ['issaziri@gmail.com']
            send_mail(subject, message, sender, recipient)
        
        context = {
            "send_mail_form":form
        }
        return render(request, 'index.html', {'context': context})


@login_required
def mentors(request):
    users_list = User.objects.filter(profile__role='mentor').order_by('username')
    paginator = Paginator(users_list, 100)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return render(request, 'core/mentors.html', {'users': users})


@login_required
def mentees(request):
    users_list = User.objects.filter(profile__role='mentee').order_by('username')
    paginator = Paginator(users_list, 100)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return render(request, 'core/mentees.html', {'users': users})


@login_required
def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    return render(request, 'core/profile.html', {
        'page_user': page_user
    })


@login_required
def initial_setup(request):
    user = request.user
    if Profile.objects.filter(is_previously_logged_in=True, user=user):
        return HttpResponseRedirect('/questions/')
    else:
        if request.method == 'POST':
            form = ProfileForm(request.POST)
            if form.is_valid():
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.profile.gender = form.cleaned_data.get('gender')
                user.profile.role = form.cleaned_data.get('role')
                user.profile.phone_number = form.cleaned_data.get('phone_number')
                user.profile.mentorship_areas = form.cleaned_data.get('mentorship_areas')
                user.email = form.cleaned_data.get('email')
                user.profile.bio = form.cleaned_data.get('bio')
                user.profile.location = form.cleaned_data.get('location')
                user.profile.highest_level_of_study = form.cleaned_data.get('highest_level_of_study')
                user.profile.profile_picture = form.cleaned_data.get('profile_picture')
                user.profile.is_previously_logged_in = True
                # image_resize(user.profile.profile_picture)
                user.save()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Your account was successfully setup.')
                return redirect('mentoring')

        else:
            form = ProfileForm(instance=user, initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'gender': user.profile.gender,
                'role': user.profile.role,
                'phone_number': user.profile.phone_number,
                'mentorship_areas': user.profile.mentorship_areas,
                'email': user.email,
                'bio': user.profile.bio,
                'location': user.profile.location,
                'highest_level_of_study': user.profile.highest_level_of_study,
                'profile_picture': user.profile.profile_picture,
            })
        return render(request, 'core/includes/initial_setup.html', {'form': form})


@login_required
def settings(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.profile.gender = form.cleaned_data.get('gender')
            user.profile.role = form.cleaned_data.get('role')
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.profile.mentorship_areas = form.cleaned_data.get('mentorship_areas')
            user.email = form.cleaned_data.get('email')
            user.profile.bio = form.cleaned_data.get('bio')
            user.profile.location = form.cleaned_data.get('location')
            user.profile.highest_level_of_study = form.cleaned_data.get('highest_level_of_study')
            user.profile.profile_picture = form.cleaned_data.get('profile_picture')
            # image_resize(user.profile.profile_picture)
            user.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Your profile was successfully edited.')

    else:
        form = ProfileForm(instance=user, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'gender': user.profile.gender,
            'phone_number': user.profile.phone_number,
            'mentorship_areas': user.profile.mentorship_areas,
            'role': user.profile.role,
            'email': user.email,
            'bio': user.profile.bio,
            'location': user.profile.location,
            'highest_level_of_study': user.profile.highest_level_of_study,
            'profile_picture': user.profile.profile_picture,
        })
    return render(request, 'core/settings.html', {'form': form})


@login_required
def password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.add_message(request, messages.SUCCESS,
                                 'Your password was successfully changed.')
            return redirect('password')

    else:
        form = ChangePasswordForm(instance=user)

    return render(request, 'core/password.html', {'form': form})