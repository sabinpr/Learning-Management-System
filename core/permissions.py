from rest_framework.permissions import BasePermission
from rest_framework.permissions import DjangoModelPermissions


class CustomModelPermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='admin').exists()


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='instructor').exists()


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='student').exists()


class IsSponsor(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='sponsor').exists()
