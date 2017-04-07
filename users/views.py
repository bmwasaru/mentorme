from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect


from .forms import SignUpForm, ProfileForm
from .tokens import account_activation_token
from.models import Profile


def account_activation_sent(request):
    return render(request, 'user/account_activation_sent.html')


def mentee_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Active your Mentor001 Account'
            message = render_to_string('user/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})


def mentor_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.groups.add(Group.objects.get(name='mentor'))
            current_site = get_current_site(request)
            subject = 'Active your Mentor001 Account'
            message = render_to_string('user/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})


def profile(request):
    if request.user.is_authenticated():
        obj = get_object_or_404(Profile, user=request.user)
        form = ProfileForm(request.POST or None, instance=obj)

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.error(
                    request, 'Your profile has been updated.', fail_silently=False)
        return render(request, 'user/profile.html', {'form': form})
    else:
        return HttpResponseRedirect("/accounts/login")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return render(request, 'user/hello.html')
    else:
        return render(request, 'user/account_activation_invalid.html')
