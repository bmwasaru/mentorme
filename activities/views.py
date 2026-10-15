from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from activities.models import Notification
from mentorme.decorators import ajax_required


def _inbox(user):
    return Notification.objects.filter(to_user=user).select_related(
        'from_user__profile', 'question', 'answer__question', 'article',
    )


@login_required
@never_cache
@require_GET
def notifications(request):
    inbox = _inbox(request.user)
    return render(request, 'activities/notifications.html', {
        'notifications': inbox, 'unread_count': inbox.filter(is_read=False).count(),
    })


@login_required
@never_cache
@require_GET
@ajax_required
def last_notifications(request):
    return render(request, 'activities/last_notifications.html', {
        'notifications': _inbox(request.user).filter(is_read=False)[:5],
    })


@login_required
@never_cache
@require_GET
@ajax_required
def check_notifications(request):
    return HttpResponse(Notification.objects.filter(to_user=request.user, is_read=False).count())


@login_required
@require_POST
def open_notification(request, pk):
    notification = get_object_or_404(_inbox(request.user), pk=pk)
    Notification.objects.filter(pk=notification.pk, to_user=request.user).update(is_read=True)
    return redirect(notification.get_target_url())


@login_required
@require_POST
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, to_user=request.user)
    Notification.objects.filter(pk=notification.pk, to_user=request.user).update(is_read=True)
    return redirect('notifications')


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(to_user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')
