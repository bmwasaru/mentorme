from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import transaction

from activities.models import Notification


@admin.action(description='Activate mentors after manual verification', permissions=['change'])
def approve_mentors(modeladmin, request, queryset):
    with transaction.atomic():
        ids = list(User.objects.filter(
            pk__in=queryset.values('pk'), profile__role='mentor', is_active=False,
        ).select_for_update(of=('self',)).values_list('pk', flat=True))
        approved = User.objects.filter(pk__in=ids).update(is_active=True)
        Notification.objects.bulk_create([
            Notification(from_user=request.user, to_user_id=pk,
                         notification_type=Notification.MENTOR_APPROVED) for pk in ids
        ])
    modeladmin.message_user(request, f'{approved} mentor account(s) activated.')


class MentorMeUserAdmin(UserAdmin):
    list_display = (*UserAdmin.list_display, 'platform_role')
    list_filter = (*UserAdmin.list_filter, 'profile__role')
    actions = [approve_mentors]

    @admin.display(description='Role', ordering='profile__role')
    def platform_role(self, user):
        return user.profile.role

    def save_model(self, request, obj, form, change):
        was_inactive = change and User.objects.filter(pk=obj.pk, is_active=False).exists()
        super().save_model(request, obj, form, change)
        if was_inactive and obj.is_active and obj.profile.role == 'mentor':
            Notification.objects.create(from_user=request.user, to_user=obj,
                                        notification_type=Notification.MENTOR_APPROVED)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


admin.site.unregister(User)
admin.site.register(User, MentorMeUserAdmin)
