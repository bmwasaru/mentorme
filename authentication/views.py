from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required
from authentication.forms import SignUpForm

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from authentication.tokens import account_activation_token

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(username=username, password=password,
                                     email=email)
            user.refresh_from_db()
            user.profile.role = form.cleaned_data.get('role')
            user.save()
            # current_site = get_current_site(request)
            # subject = 'Activate Your MySite Account'
            # message = render_to_string('authentication/account_activation_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token': account_activation_token.make_token(user),
            # })
            # user.email_user(subject, message)
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/account/login/')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'authentication/account_activation_sent.html')


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
        return redirect('/')
    else:
        return render(request, 'authentication/account_activation_invalid.html')