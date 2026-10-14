from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


@admin.action(description='Activate mentors after manual verification', permissions=['change'])
def approve_mentors(modeladmin, request, queryset):
    approved = queryset.filter(profile__role='mentor', is_active=False).update(is_active=True)
    modeladmin.message_user(request, f'{approved} mentor account(s) activated.')


class MentorMeUserAdmin(UserAdmin):
    list_display = (*UserAdmin.list_display, 'platform_role')
    list_filter = (*UserAdmin.list_filter, 'profile__role')
    actions = [approve_mentors]

    @admin.display(description='Role', ordering='profile__role')
    def platform_role(self, user):
        return user.profile.role

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


admin.site.unregister(User)
admin.site.register(User, MentorMeUserAdmin)
