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


def index(request):
    return render(request, 'core/includes/cover.html')


def donate(request):
    donate = "Working on Lipa na Mpesa form"
    return render(request, 'donate.html', {'donate': donate})


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
            try:
                send_mail(subject, message, sender, recipient)
            except BadHeaderError:
                return HttpResponse('invalid header found')
        
        context = {
            "send_mail_form":form
        }
        return render(request, 'index.html', context)


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


def personality_test_view(request):
    # form_interest = interest_form
    # form_dynamic = dynamic_form
    form_interest= InterestForm
    
    user = request.user.username

    if request.method == 'POST':
        # form1= interest_form(request.POST)
        # form2= language_form(request.POST)
        form3= InterestForm(request.POST)

        if form3.is_valid():
            # form1_instance = form1.save(commit=False)
            # form2_instance = form2.save(commit=False)
            form3_instance = form3.save(commit=False)

            # form1_instance.user = User.objects.get(username=user)
            # form2_instance.user = User.objects.get(username=user)
            form3_instance.user = User.objects.get(username=user)

            # form1_instance.save()
            # form2_instance.save()
            form3_instance.save()

            return redirect('initial_setup')

        else: 
            #find the appropriate step for if there is an error
            pass


    context = {
        'user':user,
        'interest_form': form_interest,
        # 'dynamic_form': form_dynamic,
        # 'language_form': form_language,
    }
    return render(request, 'core/includes/personality_test.html', context)


@login_required
def find_match(request):
    user = request.user
    matches = []

    ### FINDING MATCHES BASED ON INTERESTS ########

    #get the users's interests, languages and dynamics values
    user_interests = Interest.objects.filter(user=user)
    # user_languages = Language.objects.filter(user=user)
    # user_dynamics = Dynamic.objects.filter(user = user)
    user_connections = Connection.objects.filter(user = user)

    #finding previous mentor connections
    connections_list = list(user_connections.values())
    connected_mentor_ids = []
    for item in connections_list:
        items = item
        connected_mentor_ids.append(items['mentor'])
    
    #getting the names of the user's interests
    user_interest_list,user_interest_dict = object_to_list(user_interests)

    #use the field names as filter for the rest of the users and return the user objects
    match_on_interest = Interest.objects.all().exclude(user = user).filter(**user_interest_dict)
    
    #loop through all the users and get their laguages.
    for match in match_on_interest:
        match_username = match.user
        match_user = User.objects.filter(username=match_username)
        
        #getting profile pictures of various matches
        try:
            match_profile_pic = Userprofile.objects.get(user=match_user)
            if match_profile_pic is not None:
                match_profile_pic_url = match_profile_pic.profile_pic
            else:
                match_profile_pic = None
        except:
            match_profile_pic_url = None
            pass

        #gathering specific match info like username, id, interests, and languages
        match_name = match.user.first_name + ' ' + match.user.last_name
        match_id = match.user.id
        match_languages_object = Language.objects.filter(user = match_username)
        languages_list = list(match_languages_object.values())
        for item in languages_list:
            del item['user_id']
            del item['id']
            languages_dict = {key : value for key, value in item.iteritems() if value == True}
        
        match_languages = []
        for key in languages_dict:
            match_languages.append(key)

        match_info = {
            'id':match_id,
            'username':match_username,
            'name': match_name,
            'profile_pic':match_profile_pic_url,
            'interests': user_interest_list,
            'languages': match_languages,
        }
        if match_id not in connected_mentor_ids:
            matches.append(match_info)


## code to hand newsletter subscritions
    form = newsletter_subscription_form() 
    if request.method == 'POST':
        form = newsletter_subscription_form(request.POST)
        if form.is_valid():
            subject = "Newsletter Subscription"
            message = "I wat to subscribe to your newsletters" 
            sender = form.cleaned_data['email']

        recipient = ['issaziri@gmail.com']
        try:
            send_mail(subject, message, sender, recipient)
        except BadHeaderError:
            return HttpResponse('invalid header found')

###### FINDING MATCHES BASED ON PERSONALITY ###########


    #context dictionary from the retrieved data and send to the template
    context = {
        "matches":matches,
        "subscription_form":form
    }
    return render(request, 'mainapp/find_match.html', context)


def make_connection(request):
    user = request.user
    mentor = request.GET.get('mentor_username', None)
    mentor_id = request.GET.get('mentor_id', None)
    mentor_object = User.objects.get(username=mentor)

    subject = "Possible mentee connection from Machus Mentor"
    message = request.GET.get('message')
    sender = request.user.email
    
    recipient = [mentor_object.email]
    try:
        send_mail(subject, message, sender, recipient)
        new_connection = Connection(
                user=user,
                mentor=mentor_id)
        new_connection.save()
    except BadHeaderError:
        return HttpResponse('invalid header found')

    data = {
        'confirm': 'Connection complete',
    }

    return JsonResponse(data)