from rest_framework import permissions

class IsProjectOwner(permissions.BasePermission):
    """
    Custom permission to allow only the project owner to delete a project.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read permissions (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only allow owners to DELETE
        return obj.owner == request.user
