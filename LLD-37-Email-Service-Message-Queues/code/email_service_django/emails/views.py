"""
The web (PRODUCER) side. These views run on the request thread and must be FAST.

The single most important line in this whole project is:

    send_welcome_email.delay(email)

`.delay(...)` serializes the arguments, pushes a message onto Redis, and returns
IMMEDIATELY -- it does NOT wait for the email to be sent. The view returns JSON
in a millisecond or two; the actual sending happens later on the worker. That is
the entire reason message queues exist.
"""

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import DeadLetter, SentEmail
from .tasks import send_welcome_email


def home(request):
    """Plain-text landing page: how to poke this service."""
    text = (
        "Email service demo (Django + Celery + Redis)\n"
        "=============================================\n\n"
        "Enqueue a welcome email (returns instantly; the worker sends it):\n\n"
        "  GET  /signup/?email=you@example.com\n"
        "  POST /signup/   (body: email=you@example.com)\n\n"
        "Try these magic addresses and WATCH the worker terminal:\n"
        "  normal@example.com  -> sends on the first try\n"
        "  fail@example.com    -> fails a couple times, then succeeds (retry+backoff)\n"
        "  poison@example.com  -> always fails -> lands in the dead-letter table\n"
        "  (re-send normal@example.com -> second time is skipped: idempotent)\n\n"
        f"So far: {SentEmail.objects.count()} sent, "
        f"{DeadLetter.objects.count()} dead-lettered.\n"
    )
    return HttpResponse(text, content_type="text/plain")


# csrf_exempt so `curl` can POST without a CSRF token. This is ONLY acceptable
# because it's a throwaway demo endpoint. A real signup would use a proper form
# token or an authenticated API.
@csrf_exempt
def signup(request):
    """Enqueue a welcome email and return immediately."""
    email = request.GET.get("email") or request.POST.get("email")
    if not email:
        return JsonResponse(
            {"error": "pass an email, e.g. /signup/?email=you@example.com"},
            status=400,
        )

    # ---- THE POINT OF THE ENTIRE CLASS ----
    # Hand the slow work to the queue and move on. We do not send here; we do not
    # block; we do not care (right now) whether SMTP is up. The user gets an
    # instant response and the email is delivered a moment later by the worker.
    async_result = send_welcome_email.delay(email)

    return JsonResponse(
        {
            "status": "queued",          # NOT "sent" -- we haven't sent anything yet!
            "email": email,
            "task_id": async_result.id,  # you could poll this for the result
            "note": "Response returned immediately. Watch the Celery worker log "
                    "to see the email actually get sent.",
        },
        status=202,  # 202 Accepted = "I took your request, I'll do it async"
    )
