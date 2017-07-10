from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, get_object_or_404, redirect

from milestones.models import Milestone, Comment
from milestones.forms import MilestoneForm, CommentForm


@login_required
def _milestones(request, milestones, active):
    paginator = Paginator(milestones, 10)
    page = request.GET.get('page')
    try:
        milestones = paginator.page(page)
    except PageNotAnInteger:
        milestones = paginator.page(1)
    except EmptyPage:
        milestones = paginator.page(paginator.num_pages)
    return render(request, 'milestones/milestones.html', {
        'milestones': milestones,
        'active': active
    })


@login_required
def milestones(request):
    return pending(request)


# @login_required
# def milestones(request):
#     milestones = Milestone.objects.filter(user=request.user)
#     return _milestones(request, milestones, 'milestones')


@login_required
def completed(request):
    milestones = Milestone.get_completed()
    return _milestones(request, milestones, 'completed')


@login_required
def pending(request):
    milestones = Milestone.get_pending()
    return _milestones(request, milestones, 'pending')


@login_required
def all_milestones(request):
    milestones = Milestone.objects.all()
    return _milestones(request, milestones, 'all_milestones')


@login_required
def add(request):
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = Milestone()
            milestone.user = request.user
            milestone.title = form.cleaned_data.get('title')
            milestone.description = form.cleaned_data.get('description')
            milestone.start_date = form.cleaned_data.get('start_date')
            milestone.due_date = form.cleaned_data.get('due_date')
            milestone.save()
            return redirect('/milestones/')

        else:
            return render(request, 'milestones/add.html', {'form': form})

    else:
        form = MilestoneForm()

    return render(request, 'milestones/add.html', {'form': form})


@login_required
def milestone(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk)
    form = CommentForm(initial={'milestone': milestone})
    return render(request, 'milestones/milestone.html', {
        'milestone': milestone,
        'form': form
    })


@login_required
def comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            user = request.user
            comment = Answer()
            comment.user = request.user
            comment.milestone = form.cleaned_data.get('milestone')
            comment.description = form.cleaned_data.get('description')
            comment.save()
            user.profile.notify_answered(comment.milestone)
            user.profile.notify_also_answered(comment.milestone)
            return redirect('/milestones/{0}/'.format(comment.milestone.pk))
        else:
            milestone = form.cleaned_data.get('milestone')
            return render(request, 'milestones/milestone.html', {
                'milestone': milestone,
                'form': form
            })
    else:
        return redirect('/milestones/')