from django.urls import re_path, include

from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'milestone', views.MilestoneViewSet)

app_name = 'api'
urlpatterns = [
    re_path(r'^', include(router.urls)),
]
