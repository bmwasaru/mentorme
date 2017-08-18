from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from authentication.forms import SignUpForm, ForgotPasswordForm, VerifyPasswordForm
from authentication.sms import send_sms_code
from authentication.models import UserCode


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'authentication/signup.html',
                          {'form': form})
        else:
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            User.objects.create_user(username=username, password=password,
                                     email=email)
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/account/login/')
    else:
        return render(request, 'authentication/signup.html',
                      {'form': SignUpForm()})


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if not form.is_valid():
            return render(request, 'authentication/password_reset.html', {'form': form})
        else:
            phone_number = form.cleaned_data.get('phone_number')
            send_sms_code(phone_number)
            return redirect('/account/forgot_pass_confirm/')
    return render(request, 'authentication/password_reset.html',
                   {'form': ForgotPasswordForm()})


def password_reset_confirm(request):
    if request.method == 'POST':
        form = VerifyPasswordForm(request.POST)
        code = form.cleaned_data.get('code')
        user_code = UserCode.objects.get(code=code)
        if user_code:
            user = user_code.user
            #TODO: Redirect to change password
        else:
            render(request, 'authentication/password_reset_confirm.html', {'error': 'Code is wrong.'})
    return render(request, 'authentication/password_reset_confirm.html', {'fotm': VerifyPasswordForm})


def password_reset_complete(request):
    return render('authentication/password_reset_complete.html')
