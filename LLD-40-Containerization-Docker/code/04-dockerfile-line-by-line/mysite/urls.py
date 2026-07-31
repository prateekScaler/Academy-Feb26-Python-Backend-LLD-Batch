import socket
import sys

from django.http import JsonResponse
from django.urls import path


def home(request):
    """One view, built to prove WHERE it is running.

    On your laptop: hostname is your machine, python is your local version.
    Inside the container: hostname is the container id, python is the image's.
    """
    return JsonResponse({
        "message": "hello from Django",
        "hostname": socket.gethostname(),   # laptop name outside, container id inside
        "python": sys.version.split()[0],   # your local version outside, the image's inside
    })


urlpatterns = [path("", home)]
