"""
The star of the show: send_welcome_email.

This runs on the CELERY WORKER, never on the web request thread. It ties together
the four ideas from the pure-Python demo, but with the REAL tools:

  * idempotency  -> a unique row in the SentEmail table
  * retries      -> self.retry(countdown=backoff) with a max_retries cap
  * backoff      -> countdown doubles each attempt (1s, 2s, 4s, ...)
  * dead-letter  -> after the cap, write a DeadLetter row instead of crashing

To make the behaviour easy to demo, the "email address" itself decides the fate:

    normal@...   -> sends on the first try
    fail@...     -> raises a transient error a couple of times, THEN succeeds
    poison@...   -> always raises -> exhausts retries -> lands in DeadLetter
    (re-send the same normal@ address -> second time is skipped: idempotent)
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError

from .models import DeadLetter, SentEmail

# Celery routes task logging into the worker's console, so every logger.X() call
# below shows up in the terminal running `celery -A config worker`.
logger = logging.getLogger(__name__)


class TransientEmailError(Exception):
    """A 'try again later' failure -- what retries exist to absorb."""


def _idempotency_key(email):
    """The stable id that means 'the welcome email for THIS person'.

    Using the address is fine for a welcome email (one per user, ever). If a user
    could receive many of the same kind of email, you'd key on something more
    specific, e.g. f"welcome:{user_id}" or a signup-event id.
    """
    return f"welcome:{email.lower()}"


def _simulate_email_provider(email, retries):
    """Stand-in for 'call the SMTP/provider API'. Fails on purpose for the demo.

    In real code this function would not exist -- send_mail() below would just
    talk to a real provider, which occasionally fails on its own.
    """
    if "poison" in email:
        # A permanent problem (bad domain, blocked address...). It will NEVER
        # succeed, so every attempt raises -> it will end up dead-lettered.
        raise TransientEmailError("provider says: 550 recipient rejected (permanent)")
    if "fail" in email and retries < settings.EMAIL_FAIL_TIMES:
        # A transient problem for the first few attempts, then it clears up.
        raise TransientEmailError(
            f"provider says: 421 service unavailable (transient, attempt {retries + 1})"
        )
    # otherwise: no failure -> the send will go through


@shared_task(bind=True, max_retries=settings.EMAIL_MAX_RETRIES)
def send_welcome_email(self, email):
    """Send one welcome email, off the request thread.

    `bind=True` gives us `self`, which carries `self.request.retries` (how many
    times THIS job has already been retried) and the `self.retry(...)` helper.
    """
    key = _idempotency_key(email)
    attempt = self.request.retries + 1  # 1-based, for human-friendly logging

    logger.info("Processing welcome email for %s (attempt %d)", email, attempt)

    # -------------------------------------------------------------------
    # (1) IDEMPOTENCY guard. at-least-once delivery means this exact job may
    # run more than once (a redelivered crash, an accidental double-enqueue).
    # If we already sent it, do nothing -- sending twice = user gets two emails.
    # -------------------------------------------------------------------
    if SentEmail.objects.filter(idempotency_key=key).exists():
        logger.info("[idempotent] %s already sent -- skipping duplicate", email)
        return {"status": "skipped_duplicate", "email": email}

    # -------------------------------------------------------------------
    # (2) Do the work. If the provider is having a moment, retry with backoff.
    # -------------------------------------------------------------------
    try:
        _simulate_email_provider(email, self.request.retries)

        # The actual send. With the console backend this PRINTS the email to
        # this worker's log. Swap the backend (see settings.py) for real SMTP.
        send_mail(
            subject="Welcome to Scaler!",
            message=f"Hi {email}, thanks for signing up. Glad to have you!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

    except TransientEmailError as exc:
        # self.request.retries = how many retries have ALREADY happened.
        # On the first attempt it's 0; after the retry budget is used up it
        # equals max_retries. We check it OURSELVES rather than relying on
        # self.retry() to signal exhaustion: when you pass exc= to self.retry(),
        # an exhausted retry re-raises THAT exception (not MaxRetriesExceeded),
        # which would crash the task instead of dead-lettering it. Being
        # explicit here is both correct and easier to read.
        if self.request.retries >= self.max_retries:
            # -----------------------------------------------------------
            # (3) DEAD-LETTER. Out of retries. Do NOT crash the worker and do
            # NOT loop forever -- park the job for a human to look at later.
            # -----------------------------------------------------------
            logger.error(
                "[dead-letter] giving up on %s after %d attempts: %s",
                email, attempt, exc,
            )
            DeadLetter.objects.create(
                idempotency_key=key, email=email, error=str(exc), attempts=attempt,
            )
            return {"status": "dead_lettered", "email": email, "attempts": attempt}

        # Otherwise we still have retries left: schedule another attempt after a
        # growing backoff. self.retry() re-enqueues THIS job with the given
        # countdown and raises (so the code below does not run).
        backoff = settings.EMAIL_RETRY_BASE_BACKOFF * (2 ** self.request.retries)
        logger.warning(
            "[retry] send to %s failed on attempt %d: %s -- retrying in %.0fs",
            email, attempt, exc, backoff,
        )
        raise self.retry(exc=exc, countdown=backoff)

    # -------------------------------------------------------------------
    # (1, cont.) Record success so any future duplicate is skipped. The unique
    # constraint makes this safe even under a race: if another attempt already
    # inserted the row, we catch IntegrityError and treat it as 'already sent'.
    # -------------------------------------------------------------------
    try:
        SentEmail.objects.create(idempotency_key=key, email=email)
    except IntegrityError:
        logger.info("[idempotent] %s was recorded concurrently -- fine", email)
        return {"status": "skipped_duplicate", "email": email}

    logger.info("[sent] welcome email delivered to %s on attempt %d", email, attempt)
    return {"status": "sent", "email": email, "attempts": attempt}
