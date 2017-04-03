from django.contrib import admin

from .models import UserProfile, MenteeApplication, MentorApplication


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'status']
    list_filter = ['status']
    ordering = ['status']
    actions = ['approve_applications']

    def approve_applications(self, request, queryset):
        for app in queryset:
            app.approve()

    approve_applications.short_description = 'Approve Application(s)'


class MentorApplicationAdmin(ApplicationAdmin):
    pass


class MenteeApplicationAdmin(ApplicationAdmin):
    pass


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(MenteeApplication, MenteeApplicationAdmin)
admin.site.register(MentorApplication, MentorApplicationAdmin)
