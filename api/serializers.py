from django.contrib.auth.models import User
from rest_framework import serializers

from milestone.models import Milestone


class MilestoneSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Milestone
        fields = (
            'id', 'milestone', 'created_at',
            'user', 'is_finished', 'finished_at'
        )