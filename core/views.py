from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import (ChangePasswordForm, ProfileForm, 
    EducationForm, ExperienceForm, MentorshipAreaForm)
from authentication.models import Profile


def index(request): 
    return render(request, 'index.html')  


def landing(request): 
    return render(request, 'landing.html')  


def home(request):
    if request.user.is_authenticated():
        # TODO: return milestones
        return HttpResponseRedirect('/questions/')
    else:
        return render(request, 'core/includes/cover.html')


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
                user.email = form.cleaned_data.get('email')
                user.profile.bio = form.cleaned_data.get('bio')
                user.profile.location = form.cleaned_data.get('location')
                user.profile.is_previously_logged_in = True
                user.save()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Your account was successfully setup.')
                return redirect('education')

        else:
            form = ProfileForm(instance=user, initial={
            'phone_number': user.profile.phone_number,
            'role': user.profile.role,
            'bio': user.profile.bio,
            'location': user.profile.location,
            })
        return render(request, 'core/includes/initial_setup.html', {'form': form})


@login_required
def education(request):
    user = request.user
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            level_of_study = form.cleaned_data.get('level_of_study')
            institution_name = form.cleaned_data.get('institution_name')
            field_of_study = form.cleaned_data.get('field_of_study')
            ed = form.save(commit=False)
            ed.user = user
            ed.save()
            return redirect('experience')
    else:
        form = EducationForm(instance=user, )
    return render(request, 'core/includes/education.html', {'form': form})


@login_required
def experience(request):
    user = request.user
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            employer = form.cleaned_data.get('employer')
            industry = form.cleaned_data.get('industry')
            job_title = form.cleaned_data.get('job_title')
            job_description = form.cleaned_data.get('job_description')
            ex = form.save(commit=False)
            ex.user = user
            ex.save()
            return redirect('mentorship_areas')
    else:
        form = ExperienceForm(instance=user, )
    return render(request, 'core/includes/experience.html', {'form': form})


@login_required
def mentorship_areas(request):
    user = request.user
    if request.method == 'POST':
        form = MentorshipAreaForm(request.POST)
        if form.is_valid():
            mentorship_areas = form.cleaned_data.get('mentorship_areas')
            m = form.save(commit=False)
            m.user = user
            m.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Your account profile was successfully setup.')
            return redirect('questions')
    else:
        form = MentorshipAreaForm(instance=user, )
    return render(request, 'core/includes/mentorship_areas.html', {'form': form})


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
            user.email = form.cleaned_data.get('email')
            user.profile.bio = form.cleaned_data.get('bio')
            user.profile.location = form.cleaned_data.get('location')
            user.profile.profile_picture = form.cleaned_data.get('profile_picture')
            user.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Your profile was successfully edited.')

    else:
        form = ProfileForm(instance=user, initial={
            'phone_number': user.profile.phone_number,
            'role': user.profile.role,
            'bio': user.profile.bio,
            'location': user.profile.location,
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