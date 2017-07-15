from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import ChangePasswordForm, ProfileForm
from authentication.models import Profile
from interests.models import Interest


def home(request):
    if request.user.is_authenticated():
        # TODO: return milestones
        return HttpResponseRedirect('/questions/')
    else:
        return render(request, 'core/cover.html')


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
                user.profile.education = form.cleaned_data.get('education')
                user.profile.education_description = form.cleaned_data.get('education_description')
                user.profile.mentorship_areas = form.cleaned_data.get('mentorship_areas')
                # user.profile.create_interests(form.cleaned_data.get('interests'))
                user.profile.is_previously_logged_in = True
                user.save()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Your account was successfully setup.')
                return redirect('questions')

        else:
            form = ProfileForm(instance=user, initial={
            'phone_number': user.profile.phone_number,
            'role': user.profile.role,
            'bio': user.profile.bio,
            'location': user.profile.location,
            'education': user.profile.education,
            'education_description': user.profile.education_description,
            'mentorship_areas': user.profile.mentorship_areas,
            # 'interests': user.profile.get_interests,
            })
        return render(request, 'core/includes/initial_setup.html', {'form': form})
        


@login_required
def settings(request):
    user = request.user
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
            user.profile.education = form.cleaned_data.get('education')
            user.profile.education_description = form.cleaned_data.get('education_description')
            user.profile.mentorship_areas = form.cleaned_data.get('mentorship_areas')
            # user.profile.create_interests(form.cleaned_data.get('interests'))
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
            'education': user.profile.education,
            'education_description': user.profile.education_description,
            'mentorship_areas': user.profile.mentorship_areas,
            # 'interests': user.profile.get_interests,
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
