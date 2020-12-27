from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.authtoken.models import Token


class AllowAnyGet(BasePermission):
    """Allows an anonymous user access for GET requests only."""

    def has_permission(self, request, view):

        if request.user.is_anonymous and request.method == "GET":
            return (True,)

        if request.user.is_staff or request.user.is_superuser:
            return True

        return request.method in SAFE_METHODS


def check_user_authentication(request):
    """Given a request, check that the user is authenticated via a token in
    the header.
    """
    token = get_token(request)

    # Case 1: no token and auth is required, prompt the user for it
    if not token:
        return None, 401

    # Case 2: the token is not associated with a user
    try:
        token = Token.objects.get(key=token)
    except:
        return None, 403

    return token.user, 200


def get_token(request):
    """The same as validate_token, but return the token object to check the
    associated user.
    """
    # Coming from HTTP, look for authorization as bearer token
    token = request.META.get("HTTP_AUTHORIZATION")

    if token:
        token = token.split(" ")[-1].strip()
        try:
            return Token.objects.get(key=token)
        except Token.DoesNotExist:
            pass

    # Next attempt - try to get token via user session
    elif request.user.is_authenticated and not request.user.is_anonymous:
        try:
            return Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            pass
