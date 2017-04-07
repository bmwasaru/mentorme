from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test


from .forms import SignUpForm, ProfileForm
from.models import Profile


def verify_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)


def mentee_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Thank you, You have been registered as a mentor user.', fail_silently=False)
            return HttpResponseRedirect("/accounts/profile")
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})


def mentor_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.add(Group.objects.get(name='mentor'))
            messages.info(request, 'Thank you, You have been registered as a mentor user.', fail_silently=False)
            return HttpResponseRedirect("/accounts/profile")
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
                messages.info(
                    request, 'Your profile has been updated.', fail_silently=False)
        return render(request, 'user/profile.html', {'form': form})
    else:
        return HttpResponseRedirect("/accounts/login")


# @user_passes_test(lambda u: u.groups.filter(name='mentor').exists())
# def mentor_profile(request):
#     return HttpResponse("I am mentor")
