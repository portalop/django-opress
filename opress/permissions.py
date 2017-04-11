from rest_framework import permissions

from .models import IPUser
from .utils import get_ip_address


class IPUsersPermission(permissions.BasePermission):
    """
    Permission check for IPs and Users.
    """

    def has_permission(self, request, view):
        ip_addr = get_ip_address(request)
        blacklisted = IPUser.objects.filter(ip_addr=ip_addr, user=request.user).exists()
        return blacklisted
