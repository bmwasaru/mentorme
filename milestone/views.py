from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Milestone
from .forms import MilestoneForm


def index(request):
    user = request.user
    milestones = Milestone.objects.filter(user=user)
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.cleaned_data.get('milestone')
            add = form.save(commit=False)
            add.user = user
            add.save()
            return redirect('index')
    else:
        form = MilestoneForm(instance=user)

    context = {
        'form': form,
        'milestones': milestones,
    }
    return render(request, 'milestone/index.html', {'context': context})


def add(request):
    user = request.user
    # page_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.cleaned_data.get('milestone')
            add = form.save(commit=False)
            add.user = user
            # add.to_user = page_user
            add.save()
            return redirect('index')
    else:
        form = MilestoneForm(instance=user)
    return render(request, 'milestone/index.html', {'form': form})