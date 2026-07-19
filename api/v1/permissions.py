from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCreatorOrReadOnly(BasePermission):
    """Allow writes only to the object's creator; reads are open."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.created_by_id == request.user.pk
