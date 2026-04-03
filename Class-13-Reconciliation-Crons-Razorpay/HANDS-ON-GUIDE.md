# Class 13: Razorpay Payment Links, Webhooks & Reconciliation

> Build a complete payment system from scratch — create payment links, handle webhooks, and add a reconciliation cron job to catch missed payments.

**Razorpay Docs:** https://razorpay.com/docs/api/payments/payment-links/create-standard/

---

## Part 1: Razorpay Payment Links & Webhooks

In this part, you'll integrate Razorpay Payment Links into the restaurant project. Customers get a payment link via SMS/email, pay through it, and your server gets notified via a webhook.

### Pre-requisites

- The `restaurant_project` with `core`, `menu`, and `orders` apps already working
- Python 3.10+ with virtualenv
- A Razorpay account (test mode) — sign up free at https://dashboard.razorpay.com
- ngrok installed (`brew install ngrok`)

---

### Step 1: Understanding Environment Variables & Keeping Secrets Safe

API keys, database passwords, and webhook secrets should **never** be committed to git. Environment variables let you keep secrets outside your code.

#### Three Ways to Set Environment Variables

**Option A: Export in terminal (temporary — gone when terminal closes)**

```bash
export RAZORPAY_KEY_ID='rzp_test_xxxx'
export RAZORPAY_KEY_SECRET='secret_xxxx'

# Verify
echo $RAZORPAY_KEY_ID
```

**Option B: Add to shell config (persistent — loads every terminal session)**

```bash
# For zsh (macOS default):
echo "export RAZORPAY_KEY_ID='rzp_test_xxxx'" >> ~/.zshrc
echo "export RAZORPAY_KEY_SECRET='secret_xxxx'" >> ~/.zshrc
source ~/.zshrc

# For bash (Linux default):
echo "export RAZORPAY_KEY_ID='rzp_test_xxxx'" >> ~/.bashrc
source ~/.bashrc
```

**Option C: `.env` file (most common in projects)**

Create a file called `.env` in your **project root** (same folder as `manage.py`):

```
# restaurant_project/.env
RAZORPAY_KEY_ID=rzp_test_xxxx
RAZORPAY_KEY_SECRET=secret_xxxx
RAZORPAY_WEBHOOK_SECRET=whsec_xxxx
```

> **Where exactly is the `.env` file?** It sits right next to `manage.py` — NOT inside any app folder, NOT in your home directory. It's a plain text file with no extension before `.env`.
>
> ```
> restaurant_project/       ← project root
> ├── .env                  ← HERE — same level as manage.py
> ├── .gitignore            ← make sure .env is listed here!
> ├── manage.py
> ├── restaurant_project/
> ├── menu/
> ├── orders/
> └── payments/
> ```

To load `.env` automatically, install `python-dotenv`:

```bash
pip install python-dotenv
```

Then at the **top** of `settings.py`:

```python
from dotenv import load_dotenv
load_dotenv()  # reads .env file and sets environment variables
```

Now `os.environ.get()` will find your keys:

```python
import os

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
```

**Option D: Cloud platform secrets (production)**

On AWS, Heroku, GCP, etc., you set environment variables through their dashboard or CLI — never through files on the server.

```bash
# AWS Elastic Beanstalk
eb setenv RAZORPAY_KEY_ID=rzp_live_xxxx RAZORPAY_KEY_SECRET=live_secret

# Heroku
heroku config:set RAZORPAY_KEY_ID=rzp_live_xxxx

# GCP
gcloud run services update myapp --set-env-vars RAZORPAY_KEY_ID=rzp_live_xxxx
```

#### IMPORTANT: Add `.env` to `.gitignore`

```bash
echo ".env" >> .gitignore
```

If you skip this step, your API keys end up on GitHub and bots will steal them within minutes. This happens to real companies.

#### For this class — hardcode test keys directly

For speed during the exercise, we'll hardcode the test keys. **Never do this in production.**

```python
# restaurant_project/settings.py — add at the bottom
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY'
RAZORPAY_KEY_SECRET = 'YOUR_SECRET'
```

---

### Step 2: Install Razorpay & Create the Payments App

```bash
cd /path/to/restaurant_project
source venv/bin/activate

pip install razorpay
pip show razorpay   # verify — should show Name: razorpay, Version: 2.x.x
```

Create the app:

```bash
python manage.py startapp payments
```

Register in `restaurant_project/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'payments',       # <-- ADD THIS
]
```

Add to `restaurant_project/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),   # <-- ADD THIS
]
```

Add config to the **bottom** of `settings.py`:

```python
# ── Razorpay Configuration ──────────────────────────────────────
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY'
RAZORPAY_KEY_SECRET = 'YOUR_SECRET'
RAZORPAY_WEBHOOK_SECRET = ''  # We'll set this after configuring ngrok

# Base URL for callbacks — change to ngrok URL when testing webhooks
BASE_URL = 'http://127.0.0.1:8000'
```

Also update `ALLOWED_HOSTS` so ngrok works:

```python
ALLOWED_HOSTS = ['*']  # Allow all hosts in development
```

---

### Step 3: Create Payment Models

Open `payments/models.py`:

```python
import uuid
from django.db import models
from core.models import TimestampedModel
from orders.models import Order


class Payment(TimestampedModel):
    """Tracks a payment against an order."""

    class Status(models.TextChoices):
        CREATED = "created", "Created"          # Payment link created
        PAID = "paid", "Paid"                   # Payment captured
        FAILED = "failed", "Failed"             # Payment failed
        REFUNDED = "refunded", "Refunded"       # Refund issued

    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveIntegerField(help_text="Amount in paise (500 rupees = 50000)")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)

    # Razorpay references — these link OUR payment to RAZORPAY's records
    razorpay_payment_link_id = models.CharField(max_length=255, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)

    failure_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Payment {self.payment_id} | Rs.{self.amount // 100} | {self.status}"


class WebhookEvent(TimestampedModel):
    """Idempotency guard — stores each webhook event ID so we don't process twice."""

    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event_type} ({self.event_id})"
```

Run migrations:

```bash
python manage.py makemigrations payments
python manage.py migrate
```

Create `payments/urls.py` (empty for now so the server doesn't crash):

```python
from django.urls import path

urlpatterns = []
```

Verify the server starts:

```bash
python manage.py runserver
```

---

### Step 4: Payment Link + Webhook Views

Open `payments/views.py`:

```python
import json
import razorpay
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction

from orders.models import Order
from .models import Payment, WebhookEvent

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@csrf_exempt
@require_POST
def create_payment_link(request):
    """
    Creates a Razorpay Payment Link for an order.
    The link is sent to the customer via SMS/email by Razorpay itself.
    """
    data = json.loads(request.body)
    order_id = data.get('order_id')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    # Calculate amount in paise
    amount_paise = int(order.calculate_total() * 100)

    # Create Payment record in our DB
    payment = Payment.objects.create(
        order=order,
        amount=amount_paise,
        status=Payment.Status.CREATED,
    )

    # Create Razorpay Payment Link
    link_data = client.payment_link.create({
        'amount': amount_paise,
        'currency': 'INR',
        'description': f'Payment for Order #{order.id}',
        'customer': {
            'name': order.customer_name,
            'email': order.customer_email,
            'contact': order.mobile_number or '9999999999',
        },
        'notify': {
            'sms': True,
            'email': True,
        },
        'notes': {
            'order_id': str(order.id),
            'payment_uuid': str(payment.payment_id),
        },
        'callback_url': f'{settings.BASE_URL}/payments/callback/',
        'callback_method': 'get',
    })

    # Save Razorpay Payment Link ID
    payment.razorpay_payment_link_id = link_data['id']
    payment.save()

    return JsonResponse({
        'payment_link_id': link_data['id'],
        'payment_link_url': link_data['short_url'],
        'amount': amount_paise,
        'our_payment_id': str(payment.payment_id),
        'status': 'created',
    })


@csrf_exempt
def payment_callback(request):
    """
    Razorpay redirects the customer here after payment.
    This is just for UX — NOT the source of truth.
    The webhook is the source of truth.
    """
    razorpay_payment_id = request.GET.get('razorpay_payment_id', '')
    razorpay_payment_link_id = request.GET.get('razorpay_payment_link_id', '')

    return JsonResponse({
        'message': 'Payment callback received',
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_payment_link_id': razorpay_payment_link_id,
        'note': 'This is just for UX. Webhook is the source of truth.',
    })


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """
    Razorpay calls this when payment status changes.
    THIS is the source of truth for updating payment status.
    """
    payload = request.body
    signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')

    # 1. Verify signature — ensures the request is actually from Razorpay
    try:
        client.utility.verify_webhook_signature(
            payload.decode('utf-8'),
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        return HttpResponse('Invalid signature', status=400)

    event = json.loads(payload)

    # 2. Idempotency — skip if we already processed this event
    event_id = event.get('event_id', '')
    if WebhookEvent.objects.filter(event_id=event_id).exists():
        return HttpResponse('Already processed', status=200)

    # 3. Process inside a database transaction (all-or-nothing)
    try:
        with transaction.atomic():
            event_type = event.get('event', '')

            if event_type == 'payment_link.paid':
                _handle_payment_link_paid(event)
            elif event_type == 'payment.failed':
                _handle_payment_failed(event)

            # Record the event so we don't process it again
            WebhookEvent.objects.create(
                event_id=event_id,
                event_type=event_type,
                payload=event,
                processed=True,
            )

        return HttpResponse('OK', status=200)

    except Exception as e:
        # Return 500 so Razorpay retries later
        return HttpResponse(f'Error: {e}', status=500)


def _handle_payment_link_paid(event):
    """Payment link was paid — update our records."""
    payment_link = event['payload']['payment_link']['entity']
    payment_entity = event['payload']['payment']['entity']
    link_id = payment_link.get('id', '')

    try:
        payment = Payment.objects.get(razorpay_payment_link_id=link_id)
        payment.status = Payment.Status.PAID
        payment.razorpay_payment_id = payment_entity.get('id', '')
        payment.save()

        # Update order status
        payment.order.status = Order.Status.CONFIRMED
        payment.order.save()
    except Payment.DoesNotExist:
        pass


def _handle_payment_failed(event):
    """Payment failed."""
    payment_entity = event['payload']['payment']['entity']
    notes = payment_entity.get('notes', {})
    payment_uuid = notes.get('payment_uuid', '')

    try:
        payment = Payment.objects.get(payment_id=payment_uuid)
        payment.status = Payment.Status.FAILED
        payment.failure_reason = payment_entity.get('error_description', 'Unknown')
        payment.save()
    except Payment.DoesNotExist:
        pass
```

Update `payments/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('create-link/', views.create_payment_link, name='create-payment-link'),
    path('callback/', views.payment_callback, name='payment-callback'),
    path('webhook/razorpay/', views.razorpay_webhook, name='razorpay-webhook'),
]
```

Test it:

```bash
python manage.py runserver

# In another terminal:
curl -X POST http://127.0.0.1:8000/payments/create-link/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1}'
```

You should get back a JSON with `payment_link_url` — that's the link customers click to pay!

---

### Step 5: Set Up ngrok & Configure Webhooks

Razorpay needs to reach your local server to send webhooks. ngrok creates a public URL that tunnels to `localhost:8000`.

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: ngrok
ngrok http 8000
```

ngrok shows something like:

```
Forwarding  https://abc123.ngrok-free.app → http://localhost:8000
```

Now:

1. Update `BASE_URL` in `settings.py` to your ngrok URL:

```python
BASE_URL = 'https://abc123.ngrok-free.app'  # YOUR ngrok URL
```

2. Go to https://dashboard.razorpay.com → **Settings → Webhooks**
3. Click **Add New Webhook**
4. Webhook URL: `https://abc123.ngrok-free.app/payments/webhook/razorpay/`
   > **Important:** Include the full path `/payments/webhook/razorpay/` — not just the base URL!
5. Select events: `payment_link.paid` and `payment.failed`
6. Copy the **Webhook Secret** and update `settings.py`:

```python
RAZORPAY_WEBHOOK_SECRET = 'whsec_xxxxxxxxxxxx'
```

Restart the Django server after these changes.

---

### Step 6: Test the Full Payment Flow

1. **Create a payment link:**

```bash
curl -X POST http://127.0.0.1:8000/payments/create-link/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1}'
```

2. **Open the `payment_link_url`** from the response in your browser

3. **Pay using test card:**
   - Card: `4111 1111 1111 1111`
   - Expiry: Any future date
   - CVV: Any 3 digits

4. **Watch what happens:**
   - The browser redirects to your callback URL (just for UX)
   - Razorpay sends a webhook to your server (source of truth)
   - Check ngrok inspector at `http://127.0.0.1:4040` to see the webhook arrive

5. **Verify in the database:**

```bash
python manage.py shell
```

```python
from payments.models import Payment, WebhookEvent
from orders.models import Order

# Payment status should be "paid"
print(Payment.objects.values('payment_id', 'status', 'razorpay_payment_id'))

# Webhook event should be recorded
print(WebhookEvent.objects.values('event_id', 'event_type', 'processed'))

# Order status should be "confirmed"
print(Order.objects.values('id', 'status'))
```

---

### Key Concepts to Understand

**Callback vs Webhook:**
- **Callback** = browser redirect after payment. Fast, but unreliable (user can close browser).
- **Webhook** = Razorpay's server calls your server directly. This is the **source of truth**.

**Signature Verification:**
Without it, anyone could send a fake POST to your webhook URL and mark payments as "paid" without actually paying.

**Idempotency:**
Razorpay might send the same webhook twice (network issues, retries). The `WebhookEvent` table ensures we only process each event once.

**`@csrf_exempt`:**
Django's CSRF protection blocks POST requests that don't come from your own frontend forms. Since Razorpay's servers can't include a CSRF token, we exempt the webhook endpoint.

---

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'razorpay'` | `pip install razorpay` (make sure venv is active) |
| `razorpay.errors.BadRequestError` | Check key_id and key_secret are correct |
| `OperationalError: table has no column named X` | Run `python manage.py migrate payments zero` then `python manage.py migrate payments` |
| Webhook not arriving | Check ngrok is running, URL in Razorpay dashboard matches, and server is running |
| `DisallowedHost` error with ngrok | Set `ALLOWED_HOSTS = ['*']` in settings.py |
| Callback not working | Make sure `BASE_URL` is set to ngrok URL (not localhost) |
| `AttributeError: settings has no attribute 'BASE_URL'` | Add `BASE_URL = 'http://127.0.0.1:8000'` to settings.py |

---

## Part 2: Reconciliation & Cron Jobs

Webhooks handle ~99% of payment confirmations. But what about the 1% that get lost? That's where **reconciliation** comes in — a scheduled job that compares your database with Razorpay's records and fixes mismatches.

---

### Step 7: Add ReconciliationLog Model

Add this to `payments/models.py` (below the existing models):

```python
class ReconciliationLog(TimestampedModel):
    """Tracks each reconciliation run — when it ran, what it found."""

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    run_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)
    total_checked = models.PositiveIntegerField(default=0)
    mismatches_found = models.PositiveIntegerField(default=0)
    mismatches_resolved = models.PositiveIntegerField(default=0)
    details = models.JSONField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)

    def __str__(self):
        return f"Recon {self.run_id} | {self.status} | {self.mismatches_found} mismatches"
```

Run migrations:

```bash
python manage.py makemigrations payments
python manage.py migrate
```

---

### Step 8: Create the Reconciliation Management Command

Django management commands are custom scripts you can run with `python manage.py <command_name>`. They're perfect for cron jobs.

Create the directory structure:

```bash
mkdir -p payments/management/commands
touch payments/management/__init__.py
touch payments/management/commands/__init__.py
```

Create `payments/management/commands/reconcile_payments.py`:

```python
from datetime import timedelta

import razorpay
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Order
from payments.models import Payment, ReconciliationLog

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


class Command(BaseCommand):
    help = 'Reconcile stale payments with Razorpay — catches missed webhooks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours', type=int, default=1,
            help='Check payments older than N hours (default: 1)',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would change without making updates',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        cutoff = timezone.now() - timedelta(hours=hours)

        self.stdout.write(f'\n=== Reconciliation Run ===')
        self.stdout.write(f'Checking payments older than {hours} hour(s)')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes will be made\n'))

        # Start tracking this run
        recon_log = ReconciliationLog.objects.create()

        # Find payments stuck in "created" that have a Razorpay link ID
        stale_payments = Payment.objects.filter(
            status=Payment.Status.CREATED,
            razorpay_payment_link_id__gt='',
            created_at__lt=cutoff,
        )

        total = stale_payments.count()
        self.stdout.write(f'Found {total} stale payment(s)\n')

        mismatches = 0
        resolved = 0
        details = []

        for payment in stale_payments:
            try:
                # Ask Razorpay: what's the real status of this payment link?
                link = client.payment_link.fetch(payment.razorpay_payment_link_id)
                rz_status = link.get('status', '')

                detail = {
                    'payment_id': str(payment.payment_id),
                    'order_id': payment.order_id,
                    'our_status': payment.status,
                    'razorpay_status': rz_status,
                    'action': 'none',
                }

                if rz_status == 'paid' and payment.status != Payment.Status.PAID:
                    mismatches += 1
                    detail['action'] = 'updated_to_paid'

                    self.stdout.write(self.style.SUCCESS(
                        f'  MISMATCH: Payment {payment.payment_id}\n'
                        f'    Ours: "{payment.status}" → Razorpay: "paid"\n'
                        f'    → Fixing to PAID'
                    ))

                    if not dry_run:
                        payments_resp = link.get('payments', {})
                        rz_payment_id = ''
                        if payments_resp:
                            items = payments_resp if isinstance(payments_resp, list) else []
                            if items:
                                rz_payment_id = items[0].get('payment_id', '')

                        payment.status = Payment.Status.PAID
                        payment.razorpay_payment_id = rz_payment_id
                        payment.save()

                        payment.order.status = Order.Status.CONFIRMED
                        payment.order.save()
                        resolved += 1

                elif rz_status == 'expired':
                    mismatches += 1
                    detail['action'] = 'updated_to_failed'

                    self.stdout.write(self.style.WARNING(
                        f'  MISMATCH: Payment {payment.payment_id}\n'
                        f'    Ours: "{payment.status}" → Razorpay: "expired"\n'
                        f'    → Fixing to FAILED'
                    ))

                    if not dry_run:
                        payment.status = Payment.Status.FAILED
                        payment.failure_reason = 'Payment link expired (found by reconciliation)'
                        payment.save()
                        resolved += 1

                else:
                    self.stdout.write(
                        f'  OK: Payment {payment.payment_id} — '
                        f'Razorpay status: "{rz_status}" — no action needed'
                    )

                details.append(detail)

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'  ERROR: Payment {payment.payment_id} — {e}'
                ))
                details.append({
                    'payment_id': str(payment.payment_id),
                    'error': str(e),
                })

        # Finalize the log
        recon_log.status = ReconciliationLog.Status.COMPLETED
        recon_log.total_checked = total
        recon_log.mismatches_found = mismatches
        recon_log.mismatches_resolved = resolved
        recon_log.details = details
        recon_log.completed_at = timezone.now()
        recon_log.save()

        self.stdout.write(f'\n=== Summary ===')
        self.stdout.write(f'Checked:    {total}')
        self.stdout.write(f'Mismatches: {mismatches}')
        self.stdout.write(f'Resolved:   {resolved}')
        if dry_run:
            self.stdout.write(self.style.WARNING('(DRY RUN — nothing was changed)'))
        self.stdout.write('')
```

---

### Step 9: Test the Reconciliation Command

```bash
# Dry run — shows what would happen without changing anything
python manage.py reconcile_payments --dry-run

# Run for real
python manage.py reconcile_payments

# Check older payments (useful if payment was created hours ago)
python manage.py reconcile_payments --hours 0
```

Verify in the database:

```bash
python manage.py shell
```

```python
from payments.models import ReconciliationLog
for log in ReconciliationLog.objects.all():
    print(f'Run: {log.run_id} | Status: {log.status} | Checked: {log.total_checked} | Mismatches: {log.mismatches_found}')
```

---

### Step 10: Schedule with Cron

Cron is a Unix scheduler that runs commands on a schedule. The syntax is:

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *  command
```

Common examples:

| Expression       | Meaning                  |
|------------------|--------------------------|
| `* * * * *`      | Every minute             |
| `0 * * * *`      | Every hour at :00        |
| `*/15 * * * *`   | Every 15 minutes         |
| `0 0 * * *`      | Midnight daily           |
| `0 9 * * 1`      | Every Monday at 9 AM     |

#### Quick cron demo

```bash
# Set a demo cron that runs every minute
echo "* * * * * echo \"Cron ran at \$(date)\" >> /tmp/cron_demo.log" | crontab -

# Watch the log (wait ~60 seconds)
tail -f /tmp/cron_demo.log

# Clean up when done
crontab -r
rm /tmp/cron_demo.log
```

#### Schedule the reconciliation command

```bash
crontab -e
```

Add this line (adjust the path to your project):

```
0 * * * * cd /path/to/restaurant_project && /path/to/venv/bin/python manage.py reconcile_payments >> /tmp/reconcile.log 2>&1
```

This runs reconciliation every hour. Verify and clean up:

```bash
crontab -l    # list current cron jobs
crontab -r    # remove all cron jobs (when done experimenting)
```

---

### Cron in Production

| Approach | Best For | How |
|----------|----------|-----|
| **crontab + management command** | Small projects, single server | What we just did |
| **Celery Beat** | Production apps that already use Celery | Celery worker + scheduler process |
| **AWS CloudWatch Events / EventBridge** | Apps on AWS | Triggers Lambda or ECS task on schedule |
| **GCP Cloud Scheduler** | Apps on GCP | Triggers Cloud Run or Cloud Function |

---

## How Reconciliation Works in Production

In real production systems with Razorpay:

- **Settlement cycle:** Razorpay settles payments to your bank account on a **T+2 basis** (2 business days after capture).
- **Recommended reconciliation frequency:**
  - **Webhook-level:** Every 1 hour — catch missed webhooks (what we built)
  - **Settlement-level:** Daily — match Razorpay's settlement reports against your DB
  - **Financial reconciliation:** Monthly — full audit matching bank statements with PG reports
- **Razorpay Dashboard** has a built-in Reconciliation section under Reports that shows payment vs settlement mismatches.

---

## Final File Structure

```
restaurant_project/
├── manage.py
├── .env                         ← API keys (gitignored!)
├── restaurant_project/
│   ├── settings.py              ← Razorpay config + BASE_URL
│   └── urls.py                  ← payments/ URL added
├── core/
├── menu/
├── orders/
└── payments/                    ← BUILT FROM SCRATCH
    ├── models.py                ← Payment + WebhookEvent + ReconciliationLog
    ├── views.py                 ← create_payment_link, callback, webhook
    ├── urls.py                  ← 3 endpoints
    └── management/
        └── commands/
            └── reconcile_payments.py  ← Cron command
```

---

## Key Takeaways

1. **Webhooks handle ~99%** of payment confirmations (real-time, server-to-server)
2. **Reconciliation handles the ~1%** that get lost (scheduled safety net)
3. **Idempotency** prevents duplicate processing (check event_id before acting)
4. **Database transactions** ensure all-or-nothing updates
5. **Signature verification** prevents spoofed webhooks
6. **Environment variables** keep secrets out of your code

## Resources

- [Razorpay Payment Links API](https://razorpay.com/docs/api/payments/payment-links/create-standard/)
- [Razorpay Webhooks Guide](https://razorpay.com/docs/webhooks/)
- [Django Management Commands](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/)
- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)
