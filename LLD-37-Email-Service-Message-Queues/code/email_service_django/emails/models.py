"""
Two tiny bookkeeping tables. Neither stores the email body -- they just record
FACTS the task needs so it can behave correctly across retries and restarts.
"""

from django.db import models


class SentEmail(models.Model):
    """
    The IDEMPOTENCY ledger.

    Before sending, the task checks: "is there already a row for this key?"
    If yes, it skips -- the email was already sent (maybe by a previous, crashed
    attempt that got redelivered). The `unique=True` on idempotency_key is the
    real guard: even if two workers race, the database will let only ONE of them
    insert the row; the loser catches IntegrityError and treats it as "already
    sent". A set-in-memory would NOT survive a worker restart; a DB row does.
    """
    idempotency_key = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SentEmail({self.email} @ {self.sent_at:%H:%M:%S})"


class DeadLetter(models.Model):
    """
    The DEAD-LETTER table.

    When a job fails so many times that we give up (retries exhausted), we do
    NOT let the exception bubble up and crash the worker, and we do NOT retry
    forever. We record it here instead. A human (or a scheduled 'replay' job)
    can look at this table later, fix the root cause, and re-enqueue.
    """
    idempotency_key = models.CharField(max_length=255)
    email = models.EmailField()
    error = models.TextField()
    attempts = models.PositiveIntegerField(default=0)
    failed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DeadLetter({self.email}: {self.error[:40]})"
