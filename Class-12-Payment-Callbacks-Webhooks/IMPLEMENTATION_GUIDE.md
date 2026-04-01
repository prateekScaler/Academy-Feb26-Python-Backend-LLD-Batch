# Payment Integration Demo (Razorpay)

This Django app demonstrates payment gateway integration with **callbacks** and **webhooks**.

## For Class 12: Payment, Callbacks & Webhooks

---

## Quick Setup (Development)

### 1. Install Razorpay SDK

```bash
pip install razorpay
```

### 2. Get Test Credentials

1. Sign up at [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. **Important**: Toggle to **Test Mode** (top-right of dashboard)
3. Go to **Settings → API Keys**
4. Generate **Test Mode** keys (start with `rzp_test_`)
5. Copy to `settings.py`:

```python
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY_ID'
RAZORPAY_KEY_SECRET = 'YOUR_SECRET_KEY'
```

### 3. Run Migrations

```bash
python manage.py makemigrations payments
python manage.py migrate
```

### 4. Start Server

```bash
python manage.py runserver
```

---

## Understanding the SDKs

Razorpay provides **two SDKs** — one for backend, one for frontend:

### Backend SDK (Python)

**File:** `payments/views.py`

```bash
pip install razorpay
```

```python
import razorpay

# Initialize client with your API credentials
client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

# Create order (line 87 in views.py)
order = client.order.create({
    'amount': 10000,    # ₹100 in paise
    'currency': 'INR',
})

# Verify callback signature (line 153 in views.py)
client.utility.verify_payment_signature({
    'razorpay_order_id': order_id,
    'razorpay_payment_id': payment_id,
    'razorpay_signature': signature,
})

# Verify webhook signature (line 215 in views.py)
client.utility.verify_webhook_signature(body, signature, WEBHOOK_SECRET)
```

### Frontend SDK (JavaScript)

**File:** `templates/payments/demo.html` (line 7)

```html
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
```

```javascript
// Configure checkout (line 355 in demo.html)
const options = {
    key: 'rzp_test_xxx',           // Your Key ID (public)
    order_id: 'order_xxx',          // From backend SDK
    handler: function(response) {   // CALLBACK when payment succeeds
        // response.razorpay_order_id
        // response.razorpay_payment_id
        // response.razorpay_signature
        sendToBackend(response);
    }
};

// Open payment popup (line 388 in demo.html)
const rzp = new Razorpay(options);
rzp.open();
```

### SDK Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR SYSTEM                              │
├─────────────────────────────┬───────────────────────────────────┤
│     BACKEND (Python SDK)    │      FRONTEND (JS SDK)            │
├─────────────────────────────┼───────────────────────────────────┤
│                             │                                    │
│  1. client.order.create()   │                                    │
│         │                   │                                    │
│         └──── order_id ────►│  2. new Razorpay({order_id})      │
│                             │     rzp.open()                     │
│                             │         │                          │
│                             │         ▼                          │
│                             │  [Razorpay Popup]                  │
│                             │         │                          │
│  3. verify_payment_signature│◄── handler(response)              │
│                             │                                    │
│  4. verify_webhook_signature│◄── (webhook from Razorpay server) │
│                             │                                    │
└─────────────────────────────┴───────────────────────────────────┘
```

---

## Production Configuration

In production, **never hardcode credentials**. Use environment variables:

```python
# settings.py (Production)
import os

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET')

# Validate on startup
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    raise ValueError("Razorpay credentials not configured!")
```

**Setting environment variables:**

```bash
# Linux/Mac (add to ~/.bashrc or ~/.zshrc)
export RAZORPAY_KEY_ID="rzp_live_xxxxxxxxxxxx"
export RAZORPAY_KEY_SECRET="xxxxxxxxxxxxxxxxxxxx"
export RAZORPAY_WEBHOOK_SECRET="whsec_xxxxxxxxxxxx"

# Or use a .env file with python-dotenv
```

**Production checklist:**
- [ ] Use `rzp_live_` keys (not `rzp_test_`)
- [ ] HTTPS only (Razorpay requires it)
- [ ] Configure webhook secret for signature verification
- [ ] Store credentials in environment variables or secrets manager
- [ ] Enable webhook retry notifications in dashboard

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/payments/api/create-order/` | POST | Create Razorpay order |
| `/payments/api/callback/` | POST | Frontend callback after payment |
| `/payments/api/webhook/` | POST | Razorpay webhook (server-to-server) |
| `/payments/api/status/<uuid>/` | GET | Check payment status |
| `/payments/api/webhooks/` | GET | List webhook events (debug) |

---

## Flow Explanation

### Step 1: Create Order

Frontend calls your backend, backend calls Razorpay:

```bash
curl -X POST http://localhost:8000/payments/api/create-order/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000,
    "customer_email": "test@example.com",
    "customer_name": "Test User"
  }'
```

**Response:**
```json
{
  "payment_id": "uuid-xxx",
  "razorpay_order_id": "order_DBJOWzybf0sJbb",
  "razorpay_key_id": "rzp_test_xxx",
  "amount": 50000,
  "amount_rupees": 500.0,
  "currency": "INR",
  "status": "created"
}
```

### Step 2: Open Razorpay Checkout (Frontend)

Use the returned `razorpay_order_id` in frontend:

```html
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
<script>
var options = {
    "key": "rzp_test_xxx",  // from response
    "amount": 50000,         // from response
    "currency": "INR",
    "order_id": "order_xxx", // razorpay_order_id from response
    "handler": function (response) {
        // Send to your backend callback
        fetch('/payments/api/callback/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature
            })
        });
    }
};
var rzp = new Razorpay(options);
rzp.open();
</script>
```

### Step 3: Webhook (Async Confirmation)

Razorpay sends webhook to `/payments/api/webhook/` when payment is confirmed.

---

## Testing Webhooks Locally

Razorpay can't reach `localhost`. Use **ngrok**:

### 1. Install ngrok
```bash
brew install ngrok  # macOS
# or download from ngrok.com
```

### 2. Expose localhost
```bash
ngrok http 8000
```

You'll get a URL like: `https://abc123.ngrok-free.app`

### 3. Configure Webhook in Razorpay

1. Go to **Dashboard → Settings → Webhooks**
2. Add new webhook URL: `https://abc123.ngrok-free.app/payments/api/webhook/`
3. Select events:
   - `payment.captured`
   - `payment.failed`
4. Copy **Webhook Secret** to `settings.py`:

```python
RAZORPAY_WEBHOOK_SECRET = 'whsec_xxxx'
```

### 4. Test with Test Card

Use these test credentials in Razorpay checkout:
- **Card**: 4111 1111 1111 1111
- **Expiry**: Any future date
- **CVV**: Any 3 digits
- **OTP**: 754081 (test mode)

---

## Test Data

### Test Cards

| Card Number | Description |
|-------------|-------------|
| 4111 1111 1111 1111 | Successful payment |
| 5267 3181 8797 5449 | Mastercard success |
| 4000 0000 0000 0002 | Card declined |

### Test UPI
- `success@razorpay` - Successful UPI
- `failure@razorpay` - Failed UPI

---

## Code Structure

```
payments/
├── models.py      # Payment, WebhookLog models
├── views.py       # API views (create order, callback, webhook)
├── urls.py        # URL routing
├── admin.py       # Admin interface
└── README.md      # This file
```

---

## Key Concepts in Code

### 1. Payment Model (`models.py`)

The `Payment` model stores both internal and Razorpay IDs:

```python
# models.py - lines 14-56

class Payment(models.Model):
    # Our internal ID (UUID for security - can't be guessed)
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True)  # Line 30

    # Razorpay IDs (received from gateway)
    razorpay_order_id = models.CharField(...)   # Line 33 - Created when order starts
    razorpay_payment_id = models.CharField(...) # Line 34 - Received after payment
    razorpay_signature = models.CharField(...)  # Line 35 - For verification

    # Status tracking
    status = models.CharField(...)              # Line 45
    callback_received = models.BooleanField()   # Line 48
    webhook_received = models.BooleanField()    # Line 50
```

**Why `razorpay_order_id` is indexed (line 33):**
- Webhooks lookup payments by this ID
- Index makes this O(1) instead of O(n) table scan

### 2. State Machine (`models.py` lines 21-27)

Payments follow a strict state progression:

```
created → processing → completed
                    ↘ failed
```

| Status | Meaning | Who sets it? |
|--------|---------|--------------|
| `created` | Order created, payment not started | `CreateOrderView` |
| `processing` | Callback received, waiting for webhook | `CallbackView` |
| `completed` | Webhook confirmed payment | `WebhookView` |
| `failed` | Payment failed | `WebhookView` |

### 3. Idempotency — Preventing Duplicate Processing

**Problem:** Razorpay may send the same webhook multiple times (network issues, retries).

**Solution:** We use `razorpay_order_id` as a lookup key and check `webhook_received` before processing:

```python
# views.py - lines 217-241 (WebhookView)

# Find existing payment by razorpay_order_id
payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)

# Only process if we haven't already
if payment and signature_valid:
    if event_type == 'payment.captured':
        payment.mark_completed_by_webhook()  # Sets webhook_received=True
```

The `mark_completed_by_webhook()` method (line 76-81) updates status **and** sets `webhook_received=True`. If a duplicate webhook arrives, we can check this flag.

**For stricter idempotency**, you could add:
```python
# Check if already processed
if payment.webhook_received:
    return HttpResponse('Already processed', status=200)
```

### 4. Signature Verification

Two types of signatures are verified:

#### A. Callback Signature (`views.py` lines 134-144)

When user returns from Razorpay checkout, frontend sends:
- `razorpay_order_id`
- `razorpay_payment_id`
- `razorpay_signature`

We verify using the **Key Secret**:

```python
# views.py - CallbackView
razorpay_client.utility.verify_payment_signature({
    'razorpay_order_id': order_id,
    'razorpay_payment_id': payment_id,
    'razorpay_signature': signature,
})
```

**What it verifies:** The response came from Razorpay, not a hacker.

#### B. Webhook Signature (`views.py` lines 194-206)

Razorpay sends webhook with `X-Razorpay-Signature` header.

We verify using the **Webhook Secret** (different from Key Secret!):

```python
# views.py - WebhookView
razorpay_client.utility.verify_webhook_signature(
    webhook_body,           # Raw request body
    webhook_signature,      # From X-Razorpay-Signature header
    settings.RAZORPAY_WEBHOOK_SECRET
)
```

**What it verifies:** The webhook came from Razorpay servers, not an attacker.

### 5. Webhook Event Logging (`models.py` lines 91-105)

Every webhook is logged, even if invalid:

```python
# views.py - lines 225-232
WebhookLog.objects.create(
    event_type=event_type,
    razorpay_payment_id=razorpay_payment_id,
    payload=payload,           # Full JSON for debugging
    signature_valid=signature_valid,
    payment=payment,
)
```

**Why log everything?**
- Audit trail for disputes
- Debug failed webhooks
- Replay if needed
- Detect attack attempts (invalid signatures)

### 6. Always Return 200 OK (`views.py` line 244)

```python
# Always return 200 to acknowledge receipt
return HttpResponse('OK', status=200)
```

**Why?** If you return 4xx/5xx, Razorpay will retry the webhook (up to 24 hours). Return 200 to say "I received it" even if there's an error — log the error internally instead.

---

## Common Issues

### "razorpay package not installed"
```bash
pip install razorpay
```

### "Razorpay credentials not configured"
Check `settings.py` has valid keys.

### "Invalid signature" on webhook
Verify `RAZORPAY_WEBHOOK_SECRET` matches dashboard.

### Webhook not received
- Check ngrok is running
- Check webhook URL in Razorpay dashboard
- Look at Razorpay dashboard → Webhooks → Recent deliveries

---

## Admin Interface

View payments and webhooks at: http://localhost:8000/admin/

Login with superuser credentials.

---

## References

- [Razorpay API Docs](https://razorpay.com/docs/api/)
- [Razorpay Webhooks](https://razorpay.com/docs/webhooks/)
- [Test Mode](https://razorpay.com/docs/payments/payments/test-mode/)
- [Signature Verification](https://razorpay.com/docs/webhooks/validate-test/)
