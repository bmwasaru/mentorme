from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import InterestForm
from .models import Interest


@login_required
def _interests(request, interests):
    paginator = Paginator(interests, 10)
    page = request.GET.get('page')
    try:
        interests = paginator.page(page)
    except PageNotAnInteger:
        interests = paginator.page(1)
    except EmptyPage:
        interests = paginator.page(paginator.num_pages)
    return render(request, 'interests/interests.html', {
        'interests': interests,
    })


@login_required
def interests(request):
    interests = Interest.objects.all()
    return _interests(request, interests)


@login_required
def add_interest(request):
    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            interest = Interest()
            interest.user = request.user
            interest.name = form.cleaned_data.get('name')
            interest.save()
            return redirect('/interests/')

        else:
            return render(request, 'interests/add_interest.html', {'form': form})

    else:
        form = InterestForm()

    return render(request, 'interests/add_interest.html', {'form': form})