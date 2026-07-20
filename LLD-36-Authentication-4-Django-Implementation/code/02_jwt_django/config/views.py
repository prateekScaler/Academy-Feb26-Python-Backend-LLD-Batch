"""
The three views this demo needs, plus the two token views we get for free from
SimpleJWT (wired up in urls.py).

The flow you are demonstrating:

    1. POST /api/register/        -> create a user           (open to everyone)
    2. POST /api/token/           -> username+password in, access+refresh out
    3. GET  /api/me/              -> needs a valid access token
    4. POST /api/token/refresh/   -> refresh token in, fresh access token out
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterView(APIView):
    """Create a new user account.

    This has to be open to anonymous callers -- you cannot ask someone to log in
    before they are allowed to sign up. So we override the project-wide
    IsAuthenticated default with AllowAny.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # request.data is DRF's parsed body. It works the same whether the
        # client sent JSON or a form, which is why we don't touch request.POST.
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "username already taken"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # create_user() HASHES the password for us (PBKDF2 by default).
        # Never use User(password=...) or User.objects.create() here -- those
        # would store the raw password in the database.
        user = User.objects.create_user(username=username, password=password)

        # 201 Created, and note what we do NOT return: no password, no token.
        # Registering is not logging in; the client calls /api/token/ next.
        return Response(
            {"id": user.id, "username": user.username},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """Return the currently logged-in user.

    No permission_classes here, so the project default (IsAuthenticated) applies.

    This method body only ever runs if the request arrived with a header like

        Authorization: Bearer <access token>

    and SimpleJWT was able to verify it: right signature, not expired, user still
    exists. Otherwise DRF returns 401 before we get here, and request.user is
    guaranteed to be a real User -- never AnonymousUser -- inside this method.

    Notice there is no database lookup for a session and no cookie involved. The
    token itself carries the user id, and the signature is what makes it
    trustworthy. That is what "stateless authentication" means.
    """

    def get(self, request):
        return Response(
            {"id": request.user.id, "username": request.user.username}
        )


class PublicView(APIView):
    """An unprotected endpoint, for contrast.

    Hit this with no header at all and it still returns 200. Compare that with
    /api/me/, which returns 401 under the same conditions -- the difference is
    entirely this one AllowAny line.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "anyone can see this"})
