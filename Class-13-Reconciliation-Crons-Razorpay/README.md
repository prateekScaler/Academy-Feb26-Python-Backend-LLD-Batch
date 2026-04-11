# Class 13: Reconciliation, Crons & Razorpay Integration

> Webhooks aren't 100% reliable. Learn how to **reconcile** payment data, schedule **cron jobs** for automated checks, and integrate **Razorpay** end-to-end.

---

## Recap Quiz (Class 12 Fundamentals)

Before diving in, make sure you can answer these:

**Q1: A customer pays Rs.500. What amount does your backend send to Razorpay?**

**50000** (paise). Payment gateways use the smallest currency unit to avoid floating-point errors:

```python
>>> 0.1 + 0.2
0.30000000000000004    # NOT 0.3!

>>> 0.1 + 0.2 == 0.3
False                  # Python says 0.3 != 0.3

# With integers (paise), this NEVER happens:
>>> 1010 * 3
3030                   # Exactly 3030 paise = Rs.30.30. Always.
```

This is **IEEE 754 floating-point** — computers store decimals as binary fractions, and some values (like 0.1) can't be represented exactly. Integers don't have this problem.

- Razorpay docs: *"amount — in **paise**"* — [razorpay.com/docs/api/orders/create](https://razorpay.com/docs/api/orders/create/)
- Stripe docs: *"amount — in the **smallest currency unit**"* — [docs.stripe.com/api/payment_intents/create](https://docs.stripe.com/api/payment_intents/create)
- Video explainer: [Why 0.1 + 0.2 != 0.3 (YouTube)](https://www.youtube.com/watch?v=PZRI1IfStY0&t=38s)

---

**Q2: What's the difference between a Callback and a Webhook?**

| | Callback | Webhook |
|---|---------|---------|
| **How** | Browser redirect | Server-to-server POST |
| **Triggered by** | User's browser | Razorpay's servers |
| **Reliable?** | No — user can close browser | Yes — cryptographically signed |
| **Use for** | UX (show "thank you" page) | **Data** (update your DB) |

**Important:** Callback does NOT mean payment succeeded. The user could have:
- Paid successfully (callback arrives with `razorpay_payment_id`)
- Payment failed (callback still arrives with error info)
- Closed browser mid-payment (**callback never arrives**)
- Manually typed your callback URL (**fake callback, no real payment**)

**Never trust the callback to update your database.** The webhook is the source of truth.

---

**Q3: Why UUIDs instead of auto-incrementing IDs for payment records?**

Sequential IDs are **guessable**. If your payment ID is `pay_1042`, an attacker knows `pay_1041` and `pay_1043` exist. UUIDs are random and unguessable — this prevents **enumeration attacks**.

---

**Q4: Can a malicious user change Rs.5000 to Rs.1 in the frontend request?**

**Not if you design it correctly.** The frontend should only send the `order_id`. The backend calculates the amount from the order items in the database. Never trust the frontend for amounts.

---

**Q5: Why use `hmac.compare_digest()` instead of `==` for signature verification?**

A regular `==` **short-circuits** — returns False at the first mismatched character. An attacker can measure comparison time and figure out the secret one character at a time (**timing attack**). `hmac.compare_digest()` always takes the same time regardless of where the mismatch is.

---

**Q6: Your Razorpay API keys are in `settings.py`. A teammate pushes to a public repo. What's the risk?**

Anyone can find the keys via GitHub search and make API calls on your behalf. **Solution: environment variables.** Store secrets outside code:
- **Local dev:** `.env` file (in `.gitignore`) or `export` in `~/.zshrc`
- **Production:** Hosting platform config (AWS EB, Heroku, Docker env)
- **In Django:** `os.environ.get('RAZORPAY_KEY_ID')`

---

## Section 1: Why Do We Need Reconciliation?

Webhooks are the best way to get payment updates — but they're **not guaranteed** to reach your server:

- Your server was down during all retry attempts
- Network issues between PG and your server
- Your webhook endpoint returned 200 but crashed before updating DB
- PG's webhook system itself had issues (rare, but happens)

### What is Reconciliation?

**Reconciliation** = Comparing your database with the Payment Gateway's records to find and fix mismatches.

Example:

| Your Database | | Payment Gateway | |
|---|---|---|---|
| ORD-001: Rs.500 — **Paid** | | pay_001: Rs.500 — **Captured** | Match |
| ORD-002: Rs.1200 — **Pending** | | pay_002: Rs.1200 — **Captured** | **MISMATCH!** Customer paid but didn't get the product |
| ORD-003: Rs.800 — **Pending** | | pay_003: Rs.800 — **Failed** | **MISMATCH!** Payment failed, order should be cancelled |

> **If reconciliation can fix all mismatches, why not skip webhooks entirely?**
>
> Because reconciliation is polling-based — it runs at intervals (e.g., every hour). A customer could wait up to an hour before their order is confirmed. Webhooks give real-time updates (within seconds). Webhooks = primary. Reconciliation = safety net.

---

## Section 2: What Can Go Wrong?

Real failure scenarios in production:

### 1. Webhook Never Arrived
Your server was deploying when Razorpay sent the webhook. All retries failed. Customer paid Rs.5000 but order shows "pending".
- **Prevention:** Reconciliation cron job catches this.

### 2. Webhook Arrived, DB Update Failed
Your handler returned 200 OK, but the database was temporarily unavailable. PG won't retry (it thinks you handled it).
- **Prevention:** Only return 200 **after** successful DB update. If DB write fails, return 500 so PG retries.

### 3. Partial Failure
Payment succeeded, but inventory update for 1 of 3 items failed.
- **Prevention:** `transaction.atomic()` — all changes succeed or none do.

### 4. Duplicate Webhook Processing
Server was slow, Razorpay retried, you processed the same webhook twice. Customer charged once, but 2 orders created.
- **Prevention:** **Idempotency keys** — store each webhook's `event_id`. Check before processing: "Have I seen this before?"

### 5. Refund Not Recorded
Support issued refund from Razorpay dashboard. Webhook missed. Your DB shows "paid" but money was returned.
- **Prevention:** Subscribe to `refund.created` events + reconciliation cron checks refund status too.

---

## Section 3: Scheduled Jobs (Crons)

### What is a Cron Job?

A task that runs **automatically at scheduled times** — without anyone pressing a button. Named after Unix's `cron` daemon (from Greek *chronos* = time).

```
Scheduler → Triggers your code → Script runs → Sleeps until next schedule
```

### Where Are Cron Jobs Used?

| Use Case | Schedule | Example |
|----------|----------|---------|
| Payment Reconciliation | Every hour | Compare DB with Razorpay (what we're building!) |
| Email Digests | Daily 8 AM | GitHub notification summaries |
| Data Cleanup | Daily 3 AM | Delete expired sessions, temp files |
| Report Generation | Monday 6 AM | Weekly sales reports, CSV exports |
| Reminders | Every 30 mins | Abandoned cart emails |
| Database Backups | Every 6 hours | Dump DB and upload to S3 |

### Cron Syntax

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *  command
```

Special characters:
- `*` — "every" (matches all values)
- `*/15` — "every 15th" (e.g., every 15 minutes)
- `5` — "exactly 5" (specific value)
- `1,15` — "1st and 15th" (multiple values)
- `1-5` — "1 through 5" (range, e.g., Mon-Fri)

Common examples:

| Expression | Meaning |
|-----------|---------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour at :00 |
| `*/15 * * * *` | Every 15 minutes |
| `0 0 * * *` | Midnight daily |
| `0 9 * * 1` | Every Monday at 9 AM |
| `0 9,18 * * 1-5` | 9 AM and 6 PM, Mon-Fri |
| `30 2 * * 0` | Every Sunday at 2:30 AM |

> **Quiz:** What does `0 9 * * 1` mean? → "At minute **0**, hour **9**, any day, any month, on **Monday**" = **Every Monday at 9:00 AM**

### Option 1: Django Management Commands + System Cron

Write a Django command, schedule with crontab. Simple, no dependencies.

```python
# yourapp/management/commands/your_task.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of what this command does'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write('DRY RUN — no changes')
        # Your job logic here...
        self.stdout.write(self.style.SUCCESS('Done!'))

# Usage:
# python manage.py your_task
# python manage.py your_task --dry-run
```

Schedule with crontab:
```bash
crontab -e

# Run every hour:
0 * * * * cd /path/to/project && /path/to/venv/bin/python manage.py reconcile_payments >> /var/log/reconcile.log 2>&1
```

**Key caveats with system cron:**
- Always use **absolute paths** (cron doesn't know your working directory)
- **Redirect output** to a log file (`>> file.log 2>&1`)
- **Environment variables aren't loaded** (cron runs with minimal shell)
- **Test manually first** before scheduling
- **Monitor failures** (cron silently swallows errors)

### Option 2: Celery Beat (Production-Grade)

**Celery** = task queue (run code in background, retry on failure, monitor everything).
**Celery Beat** = scheduler that tells Celery *when* to run tasks.

**Why Celery over crontab?**

| | System Cron | Celery |
|---|---|---|
| Job fails? | Silent failure, no retry | **Automatic retry** with backoff |
| 3 servers? | Runs on **all 3** (duplicates!) | Shared queue — **one worker** picks it up |
| Monitoring? | Parse log files | **Dashboard** (Flower) |
| Overlap? | Two copies running | **Skip or queue** the next one |
| 50 tasks? | Blocks the server | **Distributed** across workers |

```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'reconcile-payments-hourly': {
        'task': 'orders.tasks.reconcile_payments',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

```bash
# 3 terminals needed:
redis-server                                    # Message broker
celery -A restaurant_project worker -l info     # Worker
celery -A restaurant_project beat -l info       # Scheduler
```

### Option 3: Cloud Schedulers

AWS CloudWatch Events, Google Cloud Scheduler — trigger an HTTP endpoint on a schedule. No infrastructure to manage.

### When to Use Which?

| Approach | Best For | Retry? | Monitoring? | Scales? |
|----------|----------|--------|-------------|---------|
| Crontab + Management Command | Side projects, learning | No | Manual (logs) | No |
| Celery Beat | Production apps | Yes | Yes (Flower) | Yes |
| Cloud Scheduler | Serverless, microservices | Yes | Yes (cloud dashboard) | Yes |

**TL;DR:** Learning? Use crontab. Production? Use Celery Beat. Already on cloud? Use cloud schedulers.

---

## Section 4: Integrating Razorpay Payment Gateway

### Why Razorpay? (And Not Stripe or PayPal)

| Feature | Razorpay | Stripe | PayPal |
|---------|----------|--------|--------|
| UPI Support | Native, excellent | No UPI | No UPI |
| Indian Cards/Netbanking | All Indian banks | Limited | Limited |
| INR Settlement | Direct to Indian bank | Yes (since 2023) | Higher conversion fees |
| Global Payments | India-focused | 135+ countries | 200+ countries |
| Pricing (India) | 2% per txn | 2% + Rs.2 per txn | 2.5% + fixed fee |
| Developer Experience | Excellent docs, Python SDK | Best-in-class docs | Dated, complex |
| Best For | **Indian businesses** | **Global SaaS** | **International freelancers** |

**The Big Takeaway:** Learn the **pattern**, not the PG. Every PG follows: **Create Order -> Collect Payment -> Verify -> Webhook**. Once you understand Razorpay, switching to Stripe is mostly reading their docs.

### The Payment Flow

```
1. Frontend sends POST /create-order to your backend
2. Backend creates Razorpay Order via API, gets order_id
3. Frontend opens Razorpay Checkout — user enters card/UPI
4. On success, frontend sends payment_id + signature to backend
5. Razorpay sends webhook to your backend — source of truth for DB update
```

### Step 1: Setup & Configuration

```python
# settings.py
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_...')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'secret_test_...')
RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', 'whsec_...')
```

Keys from: Razorpay Dashboard -> Settings -> API Keys

### Step 2: Database Models

```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('paid', 'Paid'),
        ('failed', 'Failed'), ('refunded', 'Refunded'),
    ]
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)

class WebhookEvent(models.Model):
    """Track processed webhooks to prevent duplicate processing"""
    razorpay_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    processed_at = models.DateTimeField(auto_now_add=True)
```

> **Why a separate WebhookEvent model?** Checking order status alone isn't enough. A `refund.created` webhook for a "paid" order would be processed — and if Razorpay retries, processed *again*. WebhookEvent tracks each unique event_id.

### Step 3: Create Razorpay Order (Backend)

```python
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreateOrderView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        order = Order.objects.create(user=request.user, amount=amount, status='pending')

        # Razorpay expects paise
        razorpay_order = client.order.create({
            'amount': int(amount * 100),
            'currency': 'INR',
            'receipt': f'order_{order.id}',
            'notes': {'order_id': order.id},
        })

        order.razorpay_order_id = razorpay_order['id']
        order.save()

        return Response({
            'order_id': order.id,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': razorpay_order['amount'],
        })
```

### Step 4: Frontend Integration

```html
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
<script>
// Get order details from backend, then:
var options = {
    key: razorpay_key_id,
    amount: amount,
    currency: "INR",
    order_id: razorpay_order_id,
    handler: function(response) {
        // Send payment_id + signature to backend for verification
        fetch('/api/verify-payment/', {
            method: 'POST',
            body: JSON.stringify({
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_signature: response.razorpay_signature
            })
        });
    }
};
var rzp = new Razorpay(options);
rzp.open();
</script>
```

### Step 5: Webhook Handler (The Important Part!)

```python
@csrf_exempt
def razorpay_webhook(request):
    payload = request.body
    signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')

    # 1. Verify signature (CRITICAL!)
    try:
        client.utility.verify_webhook_signature(
            payload.decode('utf-8'), signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        return HttpResponse(status=400)

    event = json.loads(payload)

    # 2. Idempotency check
    event_id = event.get('event_id', '')
    if WebhookEvent.objects.filter(razorpay_event_id=event_id).exists():
        return HttpResponse(status=200)  # Already processed

    # 3. Process in transaction
    try:
        with transaction.atomic():
            if event['event'] == 'payment.captured':
                handle_payment_success(event['payload']['payment']['entity'])
            elif event['event'] == 'payment.failed':
                handle_payment_failure(event['payload']['payment']['entity'])

            WebhookEvent.objects.create(
                razorpay_event_id=event_id, event_type=event['event']
            )
        return HttpResponse(status=200)
    except Exception:
        return HttpResponse(status=500)  # PG will retry
```

### Step 6: Testing Webhooks Locally

```bash
# 1. Start Django
python manage.py runserver

# 2. Expose via ngrok
ngrok http 8000
# Output: https://abc123.ngrok-free.app -> http://localhost:8000

# 3. Razorpay Dashboard -> Webhooks -> Add New Webhook
#    URL: https://abc123.ngrok-free.app/api/webhook/razorpay/
#    Events: payment.captured, payment.failed, refund.created

# 4. Test payment with card: 4111 1111 1111 1111, any expiry, any CVV
```

---

## Section 5: Putting It All Together

### Payment System Architecture

**Happy Path (99% of transactions):**
```
User clicks "Pay" → Backend creates Order → Razorpay Checkout
    → Payment Done → Webhook (payment.captured) → DB Updated (status = "paid")
```

**Safety Net (when webhooks fail ~1%):**
```
Webhook Failed → Cron Job (every hour) → Fetches from Razorpay API
    → Compares DB vs Razorpay → Fixes Mismatches → Alerts Team (if many)
```

### Key Principles

- **Primary: Webhooks** — real-time, event-driven
- **Backup: Reconciliation** — catches missed webhooks
- **Alert: On Anomalies** — many mismatches = something is wrong
- **Audit: Log Everything** — debug trail for every transaction

### How Reconciliation Works at Scale

| Level | Frequency | What It Does |
|-------|-----------|-------------|
| **Webhook-level** | Every 1 hour | Catches missed webhooks (what we built today) |
| **Settlement-level** | Daily | Razorpay settles on **T+2 basis**. Match settlement reports against DB |
| **Financial reconciliation** | Monthly | Full audit — match bank statements with PG reports |

**What merchants actually do:**
- **Daily CSV download:** Small-medium merchants download transaction reports from Razorpay Dashboard -> Reports -> Transactions
- **Settlement matching:** When Razorpay settles to your bank (T+2), match their settlement report against your bank statement
- **Automated via API:** Large merchants (Swiggy, Zomato) build automated pipelines using Razorpay's `/settlements/recon/combined` API
- **Third-party tools:** Dedicated reconciliation services that connect to Razorpay's API

**Key insight:** No matter how automated your webhooks are, you always need reconciliation because money moving through banks is a different system from payment status updates.

### Production Checklist

- [ ] Store API keys in environment variables
- [ ] Verify webhook signatures
- [ ] Implement idempotency (WebhookEvent model)
- [ ] Use database transactions in webhook handler
- [ ] Return 200 only after successful DB update
- [ ] Set up reconciliation cron job
- [ ] Add logging for debugging
- [ ] Test with ngrok + Razorpay test mode
- [ ] Set up alerts for high mismatch rates
- [ ] Handle refunds and disputes

---

## Quick Quiz

**Q1:** Why store `razorpay_event_id` in the database?
> To prevent duplicate processing (idempotency).

**Q2:** Why return 500 (not 200) when the webhook handler crashes?
> So Razorpay retries. Returning 200 means "I handled it" — PG won't retry.

**Q3:** Why both webhooks AND reconciliation?
> Webhooks = real-time but not 100% reliable. Reconciliation = backup. Belt and suspenders.

**Q4:** Cron runs hourly. Customer pays at 2:01 PM, webhook fails. When is order updated?
> The 3:00 PM cron checks payments older than 1 hour, so the 2:01 PM payment won't qualify until after 3:01 PM. In practice, the **4:00 PM** run catches it.

**Q5:** Building SaaS for US, Europe, and India — which PG(s)?
> **Stripe** for US/Europe, **Razorpay** for India (UPI is a must). Many companies use multiple PGs for different regions.

---

## Resources

- [Razorpay Payment Links API](https://razorpay.com/docs/api/payments/payment-links/create-standard/)
- [Razorpay Webhooks Guide](https://razorpay.com/docs/webhooks/)
- [Razorpay Settlements API](https://razorpay.com/docs/api/settlements/)
- [Django Management Commands](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/)
- [Celery Documentation](https://docs.celeryq.dev/)

---

*For the hands-on implementation guide, see [HANDS-ON-GUIDE.md](HANDS-ON-GUIDE.md)*
