from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('users.urls')),
]

admin.site.site_title = 'Mentor001 Adminstration'
admin.site.site_header = 'Mentor001 Adminstration'
