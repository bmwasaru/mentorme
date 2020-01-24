from rest_framework import permissions, viewsets

from api.serializers import MilestoneSerializer
from milestone.models import Milestone


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # If the object doesn't have a user (i.e. anon) allow all methods.
        if not obj.user:
            return True

        # Instance must have an attribute named `user`.
        return obj.user == request.user


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = (IsCreatorOrReadOnly,)

    def perform_create(self, serializer):
        user = self.request.user
        user = user if user.is_authenticated else None
        serializer.save(user=user)
