"""
Four tiny views, each demonstrating one idea.

Read them in order: index -> submit -> api_ping -> unsafe_submit.
"""
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def index(request):
    """Render the demo page (templates/index.html).

    This is a GET request. GET is a "safe" method, so Django's CSRF
    middleware does not check anything here -- it only guards POST, PUT,
    PATCH and DELETE.
    """
    return render(request, "index.html")


def submit(request):
    """The form's POST target -- protected by CsrfViewMiddleware.

    How the protection works:
      1. When index.html rendered, `{% csrf_token %}` put a hidden input named
         `csrfmiddlewaretoken` in the form, and Django set a `csrftoken` cookie.
      2. On POST, CsrfViewMiddleware compares the hidden field against the
         cookie. They must match.
      3. If the field is missing or wrong -> Django returns **403 Forbidden**
         and this function is never even called.

    Why that stops CSRF: an attacker's page on evil.com can make your browser
    send a POST here (browsers happily send cookies along), but it cannot READ
    your token -- the same-origin policy blocks it. No token, no 403-free POST.
    """
    if request.method != "POST":
        return HttpResponse("Send a POST from the form on the home page.", status=405)

    name = request.POST.get("name", "")
    return HttpResponse(
        f"✅ CSRF token was valid — form accepted (name={name!r})",
        content_type="text/plain; charset=utf-8",
    )


def api_ping(request):
    """A JSON endpoint, used to demonstrate CORS.

    Fetch this from the demo page (same origin) -> always works; CORS is not
    even involved, because same-origin requests are not "cross-origin".

    Fetch it from a page served on a DIFFERENT origin (say
    http://localhost:5500) -> the browser sends the request, the server runs
    this function and replies, and then the browser decides whether the calling
    JavaScript is allowed to READ the reply, based on the
    Access-Control-Allow-Origin header that django-cors-headers added.
    """
    return JsonResponse({
        "pong": True,
        "message": "CORS lets the browser decide who may READ this JSON.",
        "method": request.method,
    })


@csrf_exempt  # ⚠️ turns OFF Django's CSRF check for this view
def unsafe_submit(request):
    """DEMO OF WHAT NOT TO DO.

    ⚠️ Never use @csrf_exempt on a state-changing endpoint (anything that
    writes to the database, transfers money, changes a password, deletes data).
    Without the token check, any website in the world can make a logged-in
    visitor's browser POST here, and the request will succeed.

    Legitimate uses are rare and always come with a *different* proof of
    intent -- e.g. a webhook that verifies an HMAC signature, or a stateless
    API that authenticates with an `Authorization: Bearer ...` header instead
    of cookies (no cookie = no CSRF surface).
    """
    return HttpResponse(
        "⚠️ Accepted with NO CSRF check — this endpoint is forgeable.",
        content_type="text/plain; charset=utf-8",
    )
