from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required
from authentication.forms import SignUpForm


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
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/account/login/')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})