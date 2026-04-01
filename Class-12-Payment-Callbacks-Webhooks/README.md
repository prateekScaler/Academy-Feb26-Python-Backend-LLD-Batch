# Class 12: Payment Integration, Callbacks & Webhooks

Use this to revise before interviews or when you need a refresher.

---

## Pre-Class Quiz: Test Your Class 9 Knowledge

### Question 1: Middleware Order
Your Django app has these middleware (in order): AuthMiddleware, LoggingMiddleware, RateLimitMiddleware. A request comes in.
**In what order do they process the REQUEST?**

<details>
<summary>Answer</summary>

**Auth → Logging → RateLimit (top to bottom)**

Middleware processes requests in the order listed in `MIDDLEWARE`. Responses go in reverse order.
</details>

---

### Question 2: Decorator vs Middleware
You want to verify a signature on incoming webhook requests, but only on 2 specific endpoints.
**Should you use middleware or a decorator?**

<details>
<summary>Answer</summary>

**Decorator** - because you only need it on specific views, not globally.

Middleware = applies to ALL requests. Decorator = you choose which views.
</details>

---

### Question 3: Exception Re-raising
```python
try:
    process_payment()
except PaymentError as e:
    logger.error(f"Payment failed: {e}")
    raise
```
**What does the bare `raise` do?**

<details>
<summary>Answer</summary>

**Re-raises the same exception** so calling code can handle it.

The error is logged, but the exception continues up the call stack. This is useful for logging without swallowing errors.
</details>

---

## Learning Objectives

By the end of this class, you will:

1. Understand why payment integration is fundamentally different from regular CRUD
2. Design payment models with proper state management
3. Know the difference between callbacks and webhooks
4. Implement secure webhook handlers with signature verification
5. Handle idempotency to prevent duplicate payments
6. Understand how Stripe and Razorpay work at a high level

---

## 💻 Live Demo Code

The working Razorpay implementation is in the **restaurant project**:

```
restaurantproject/payments/
├── models.py          # Payment + WebhookLog models
├── views.py           # CreateOrder, Callback, Webhook views (with SDK usage)
├── urls.py            # API endpoints
├── admin.py           # Admin interface
└── templates/payments/
    └── demo.html      # Frontend with Razorpay checkout.js
```

**Key files to review:**
- `views.py` lines 55-60: Backend SDK initialization
- `views.py` lines 87-103: Creating Razorpay order
- `views.py` lines 153-160: Verifying callback signature
- `views.py` lines 215-232: Verifying webhook signature
- `demo.html` line 7: Frontend SDK include
- `demo.html` lines 355-388: Opening Razorpay checkout

See `INSTRUCTOR.md` for step-by-step demo instructions.

---

## 🛠️ Tools You'll Need for This Class

| Tool | Purpose | Link |
|------|---------|------|
| **ngrok** | Expose your localhost to receive webhooks | https://ngrok.com |
| **Razorpay Test Mode** | Test payments without real money | https://dashboard.razorpay.com |

### Testing Webhooks Locally

Razorpay can't reach `localhost`. Use ngrok to create a tunnel:

```bash
# Terminal 1: Start ngrok
ngrok http 8000
# Copy the https URL, e.g., https://abc123.ngrok-free.app

# Terminal 2: Start Django
python manage.py runserver
```

Then configure webhook in Razorpay Dashboard → Settings → Webhooks:
- URL: `https://abc123.ngrok-free.app/payments/api/webhook/`
- Events: `payment.captured`, `payment.failed`

---

## Why Payments Are Different

Regular CRUD:
```
Client → Your Server → Database → Response
(Synchronous, you control everything)
```

Payments:
```
Client → Your Server → Payment Gateway → Bank → Response
                ↓
        (Gateway calls YOU back later via webhook)
```

**Three things make payments hard:**

| Challenge | Description |
|-----------|-------------|
| **External Systems** | You don't control the payment gateway or banks |
| **Asynchronous** | Payment status can change minutes/hours later |
| **Money** | Bugs mean real financial loss, not just bad UX |

---

### 🧠 Think About It: Why Not Just Use AJAX?

**Question:** You could just make an AJAX call to the payment gateway and wait for the response. Why do we need this complicated webhook system?

<details>
<summary>Think first, then click for answer</summary>

**Several reasons:**

1. **Timeouts** - Bank verification can take 30+ seconds. HTTP requests timeout.
2. **Network failures** - What if the response is lost? Payment happened but you don't know.
3. **3D Secure / OTP** - User might take 2 minutes to enter OTP. Can't hold connection that long.
4. **Retries** - If your server crashes during processing, webhooks will retry. AJAX won't.

This is why payment gateways use the **async webhook pattern** - it's more reliable for long-running, critical operations.

</details>

---

## 🏗️ Architecture Decision: Who Calls the Payment Gateway?

This is a common interview question and an important design decision. Let's break it down.

### Question 1: Frontend or Backend?

**Should the frontend (React/mobile app) call Stripe/Razorpay directly, or should it go through your backend?**

```
Option A: Frontend → Payment Gateway (Direct)
Option B: Frontend → Your Backend → Payment Gateway
```

<details>
<summary>Answer: It's BOTH (but different responsibilities)</summary>

**The standard pattern uses BOTH, but for different things:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    STANDARD PAYMENT FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Frontend calls YOUR BACKEND to create order/intent          │
│         │                                                        │
│         ▼                                                        │
│  2. Backend creates Payment Intent with gateway                  │
│     Backend returns client_secret / order_id to frontend        │
│         │                                                        │
│         ▼                                                        │
│  3. Frontend uses client_secret to open gateway checkout        │
│     (Stripe.js / Razorpay.js - runs in browser)                 │
│         │                                                        │
│         ▼                                                        │
│  4. User enters card on GATEWAY's iframe (PCI compliant)        │
│         │                                                        │
│         ▼                                                        │
│  5. Gateway sends webhook to YOUR BACKEND                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Why this split?**

| Step | Who | Why |
|------|-----|-----|
| Create intent | Backend | Amount validation, fraud checks, audit logs |
| Collect card | Frontend (gateway JS) | PCI compliance - you never touch card data |
| Confirm payment | Webhook to Backend | Reliable, server-to-server |

**Never do this:**
```javascript
// ❌ BAD: Frontend decides the amount
fetch('https://api.stripe.com/create-payment', {
    amount: 100  // User can modify this in browser!
})
```

**Always do this:**
```javascript
// ✅ GOOD: Backend decides the amount
// Frontend
const response = await fetch('/api/create-payment-intent', {
    orderId: 'order_123'
});
const { clientSecret } = response.json();
// Backend looked up order_123 and set amount = ₹500
```

</details>

---

### Question 2: Order Service → Payment Service → Gateway?

**In a microservices architecture, should OrderService call PaymentService, or should PaymentService directly integrate with Stripe/Razorpay?**

```
Option A: OrderService → Stripe (direct)
Option B: OrderService → PaymentService → Stripe
```

<details>
<summary>Answer: Option B (Payment Service as abstraction)</summary>

**Almost every production system uses a dedicated Payment Service. Here's why:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MICROSERVICES PATTERN                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   OrderService ──┐                                               │
│                  │                                               │
│   CartService ───┼──→ PaymentService ──→ Stripe / Razorpay      │
│                  │          │                                    │
│   SubscriptionService ─────┘         │                          │
│                                      ▼                          │
│                              PaymentService stores:              │
│                              - Transaction logs                  │
│                              - Retry logic                       │
│                              - Gateway abstraction               │
│                              - Idempotency keys                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits of a dedicated Payment Service:**

| Benefit | Explanation |
|---------|-------------|
| **Single integration point** | Only PaymentService knows Stripe API. If Stripe changes, update one service. |
| **Gateway abstraction** | Switch from Stripe to Razorpay without touching OrderService |
| **Centralized audit logs** | All payment attempts in one place for compliance |
| **Retry & idempotency** | One place to handle duplicate webhooks, retries |
| **Rate limiting** | Control API calls to gateway from one service |
| **PCI scope reduction** | Only PaymentService needs PCI compliance review |

**Example interface:**

```python
# OrderService just calls PaymentService API
class OrderService:
    def checkout(self, order_id):
        response = payment_service.create_payment(
            order_id=order_id,
            amount=self.calculate_total(order_id),
            currency='INR',
            metadata={'order_id': order_id}
        )
        return response.checkout_url

# PaymentService handles ALL gateway logic
class PaymentService:
    def create_payment(self, order_id, amount, currency, metadata):
        # Could be Stripe, Razorpay, or any gateway
        # OrderService doesn't know or care
        if self.gateway == 'stripe':
            return self._create_stripe_session(...)
        elif self.gateway == 'razorpay':
            return self._create_razorpay_order(...)
```

**When might you skip PaymentService?**
- Very early startup (< 10 engineers)
- Single product, single payment flow
- No plans to change gateways

But even then, at least abstract the gateway behind an interface!

</details>

---

## 🎯 Where Does the User Actually Enter Card Details?

This is where confusion often happens. It's **not always** a full redirect to the gateway's page. There are three common patterns:

### Pattern 1: Full Redirect (D2C Websites, Small Merchants)

User clicks "Pay" → Browser redirects to `checkout.stripe.com` or `razorpay.com/pay/...` → User enters card details there → Redirects back to your site.

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Your Site     │ ───→ │  Stripe.com     │ ───→ │   Your Site     │
│   "Pay Now"     │      │  Card Input     │      │   "Thank You"   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

**Examples:** Small D2C brands, indie e-commerce, subscription sites
**PCI Compliance:** Easiest - you never see card data
**User Experience:** Slight friction (user leaves your site)

---

### Pattern 2: Embedded iframe / Drop-in Widget (Shopify, Frido, Most Modern Sites)

The page *looks like* it belongs to the merchant — you see the merchant's branding, discount code fields, address fields, order summary. But the actual **card input field is an iframe** served by the payment gateway, embedded inside the merchant's page.

```
┌─────────────────────────────────────────────────────────────────┐
│                     MERCHANT'S CHECKOUT PAGE                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Shipping Address: [Your own field]                         ││
│  │  Discount Code: [Your own field]  [APPLY]                   ││
│  │  ─────────────────────────────────────────────────────────  ││
│  │  Order Summary:                                             ││
│  │    Product A ............................ ₹500              ││
│  │    Discount (-10%) ...................... -₹50              ││
│  │    Total ................................ ₹450              ││
│  │  ─────────────────────────────────────────────────────────  ││
│  │                                                              ││
│  │  ┌─────────────────────────────────────────────────────┐    ││
│  │  │░░░░░░░░░░░░░░░░ STRIPE IFRAME ░░░░░░░░░░░░░░░░░░░░░│    ││
│  │  │  Card Number: [4242 4242 4242 4242]                 │    ││
│  │  │  Expiry: [12/28]    CVV: [123]                      │    ││
│  │  │  (This goes DIRECTLY to Stripe servers)             │    ││
│  │  └─────────────────────────────────────────────────────┘    ││
│  │                                                              ││
│  │              [ PAY ₹450 ]                                    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

**The key insight:** The discount code field, address fields, order summary — all merchant's HTML. But the card number, expiry, CVV fields are inside a tiny **iframe** that Stripe serves from `js.stripe.com`.

Your card data goes **directly from that iframe to Stripe's servers**. The merchant's JavaScript literally **cannot read** what's inside that iframe due to browser same-origin policy.

This is called **Stripe Elements** or **Razorpay Inline Checkout**.

**Examples:** Shopify stores, Frido, Boat, most modern e-commerce
**PCI Compliance:** Easy - card data never touches your servers
**User Experience:** Seamless - user stays on your site

---

### Pattern 3: Direct API (Amazon, Netflix, Big Companies Only)

Companies like Amazon or Netflix actually collect card data on their own servers and send it to the processor via API.

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Amazon.com    │ ───→ │ Amazon Servers  │ ───→ │ Payment Network │
│   Card Input    │      │ (PCI Certified) │      │ (Visa/MC/etc)   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

This requires **PCI DSS Level 1 certification**, which is extremely expensive and painful:
- Annual security audits ($50K-$200K)
- Network segmentation
- Quarterly penetration testing
- Dedicated security team
- Encrypted storage for card data

**Examples:** Amazon, Netflix, Uber (companies processing millions of transactions)
**PCI Compliance:** Maximum burden - full responsibility
**User Experience:** Complete control over UX

---

### 🧠 Quiz: What Pattern is This?

You're shopping on a Shopify store. You see the store's branding everywhere. There's a discount code field that applies instantly. The card input field looks like it matches the site's design.

**Where is your card data going when you type?**

<details>
<summary>Answer</summary>

**Pattern 2: Embedded iframe**

Even though it *looks* like the merchant's site, that card field is actually a Stripe iframe. Your keystrokes go directly to Stripe, not the merchant's server.

The discount code field? That's the merchant's code. The card field? That's Stripe's code in a seamless iframe.

This is why small merchants can have beautiful, integrated checkouts without handling card data themselves.

</details>

---

## 🔄 Callback AND Webhook — Both Happen Together!

A common confusion: "Is it callback OR webhook?"

**Answer: Both happen together.** They serve different purposes.

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOTH HAPPEN SIMULTANEOUSLY                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User pays on gateway                                           │
│         │                                                        │
│         ├─────────────────────────────────────────┐              │
│         │                                         │              │
│         ▼                                         ▼              │
│  ┌──────────────────┐                 ┌──────────────────┐      │
│  │  CALLBACK (6a)   │                 │  WEBHOOK (6b)    │      │
│  │  Browser Redirect│                 │  Server POST     │      │
│  │                  │                 │                  │      │
│  │  User's browser  │                 │  Gateway server  │      │
│  │  goes to your    │                 │  POSTs to your   │      │
│  │  /success page   │                 │  /webhook        │      │
│  │                  │                 │                  │      │
│  │  PURPOSE:        │                 │  PURPOSE:        │      │
│  │  Show user       │                 │  Update your     │      │
│  │  "Thank You"     │                 │  database        │      │
│  └──────────────────┘                 └──────────────────┘      │
│                                                                  │
│  ⚠️ DON'T trust this                  ✅ TRUST this             │
│  (user can fake URL)                  (cryptographically signed) │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why Both?

| Mechanism | What it's for | Can you trust it? |
|-----------|---------------|-------------------|
| **Callback** | User experience - show "Thank You" or "Try Again" page | ❌ No - user can type /success URL directly |
| **Webhook** | Server truth - update database, send emails, grant access | ✅ Yes - signed, verified |

### The Real Flow in Practice

```
1. User pays on Stripe
2. Stripe sends webhook to your /webhook endpoint (async, 2-30 seconds)
3. Stripe redirects user's browser to your /success page (sync, immediate)
4. Your /success page checks:
   - Did webhook already update the payment status? → Show "Thank You"
   - Not yet? → Poll for a few seconds, or show "Verifying..."
```

### 🧠 Quiz: What If Webhook Arrives After Redirect?

User pays successfully. Browser redirects to your `/success` page. But the webhook hasn't arrived yet (network delay).

**What should your `/success` page do?**

<details>
<summary>Answer</summary>

**Options (in order of preference):**

1. **Poll/Refresh** - Check payment status every 2 seconds for up to 30 seconds
```python
# Frontend polls
GET /api/payment/{id}/status
# Returns 'pending' → 'completed' eventually
```

2. **Show "Verifying"** - Honest message while webhook is processed
```html
"Payment received! We're confirming your order..."
```

3. **Optimistic UI with email fallback** - Show success, confirm via email
```html
"Thank you! Check your email for order confirmation."
```

**Never:** Trust the callback alone and immediately say "Payment successful!" without webhook verification.

</details>

---

### 🧠 Quiz: Why Not Let Frontend Call Gateway Directly?

A junior developer suggests: "Why not just call Stripe from React? It's simpler!"

```javascript
// Their proposal
const payment = await stripe.createPayment({
    amount: cart.total,
    currency: 'inr'
});
```

**What are the problems with this approach?**

<details>
<summary>Answer</summary>

**Multiple serious problems:**

1. **Amount tampering** - User can open DevTools and change `cart.total` to ₹1
2. **No audit trail** - Your backend has no record of the payment attempt
3. **No validation** - Can't verify inventory, apply discounts, check fraud
4. **Secrets exposure** - API keys in frontend code can be stolen
5. **No idempotency** - Can't prevent duplicate payments on retry
6. **Webhook mismatch** - Webhook arrives but backend doesn't know about this payment

**The ONLY thing frontend should do with payment gateway:**
- Render the checkout UI (using their SDK)
- Pass the `client_secret` your backend generated

</details>

---

## Restaurant Analogy

Think of payment like settling the bill at a restaurant:

| Payment Concept | Restaurant Equivalent |
|-----------------|----------------------|
| Payment Intent | Customer asks for the check |
| Processing | Waiter runs the card |
| Webhook | Kitchen gets notified payment succeeded |
| Callback | Waiter returns with receipt |
| Refund | Manager processes a return |
| Reconciliation | End-of-day cash register count |

---

## Payment Flow: The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PAYMENT FLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. User clicks "Pay"                                           │
│         │                                                        │
│         ▼                                                        │
│  2. Your Server creates Payment Intent                          │
│         │                                                        │
│         ▼                                                        │
│  3. Redirect to Gateway (Stripe Checkout / Razorpay)            │
│         │                                                        │
│         ▼                                                        │
│  4. User enters card details (on GATEWAY's page, not yours!)    │
│         │                                                        │
│         ▼                                                        │
│  5. Gateway processes with bank                                 │
│         │                                                        │
│         ├──────────────────────┐                                │
│         ▼                      ▼                                │
│  6a. Callback (sync)     6b. Webhook (async)                    │
│      User redirected         Gateway POSTs to                   │
│      back to your site       your /webhook endpoint             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Critical:** Never trust the callback alone! Users can close their browser before the redirect. Always rely on webhooks for confirmation.

---

### 🧠 Scenario: The Disappearing Customer

**Question:** A customer completes payment on Razorpay, but closes their browser before the redirect to your success page. What happens?

A) Payment is reversed automatically
B) Payment succeeds, but your database shows "pending"
C) Payment fails because redirect didn't complete
D) Razorpay holds the payment until redirect succeeds

<details>
<summary>Answer</summary>

**B) Payment succeeds, but your database shows "pending"**

The payment happened at Razorpay's end - that's complete. The callback redirect is just a UI convenience. This is exactly why you **must** rely on webhooks, not callbacks, to update your database.

Without webhook handling, you'd have a paid customer whose order shows as "unpaid" - very bad UX and potential support nightmare!

</details>

---

## Transaction States

Payments have states. You can't jump randomly between them.

```
                    ┌──────────────┐
                    │   PENDING    │
                    │  (created)   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PROCESSING  │
                    │  (sent to    │
                    │   gateway)   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ COMPLETED│ │  FAILED  │ │ EXPIRED  │
       │    ✓     │ │    ✗     │ │    ⏰    │
       └────┬─────┘ └──────────┘ └──────────┘
            │
            ▼
       ┌──────────┐
       │ REFUNDED │
       │    ↩     │
       └──────────┘
```

---

## Payment Model Design

```python
# payments/models.py

from django.db import models
from orders.models import Order
import uuid


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'
    EXPIRED = 'expired', 'Expired'


class Payment(models.Model):
    # Your internal ID (never expose auto-increment IDs for payments!)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to order
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='payments')

    # Amount in smallest currency unit (paise/cents)
    amount = models.PositiveIntegerField()  # 1000 = ₹10.00 or $10.00
    currency = models.CharField(max_length=3, default='INR')  # ISO 4217

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    # Gateway reference (store their ID!)
    gateway = models.CharField(max_length=50)  # 'stripe', 'razorpay'
    gateway_payment_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_order_id = models.CharField(max_length=255, blank=True, null=True)

    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Metadata (for debugging)
    metadata = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['gateway_payment_id']),
            models.Index(fields=['order', 'status']),
        ]
```

**Key design decisions:**

1. **UUID primary key** - Don't expose sequential IDs for financial data
2. **Amount in smallest unit** - Avoid floating point issues (₹10.00 = 1000 paise)
3. **Store gateway IDs** - You'll need these for debugging and reconciliation
4. **Status choices** - Use TextChoices for type safety
5. **Audit timestamps** - Track when each state change happened
6. **PROTECT on delete** - Never cascade-delete payment records

---

### 🧠 Why UUID for Payments?

**Question:** We use `models.AutoField` (sequential IDs like 1, 2, 3...) for most models. Why use UUID for payments?

<details>
<summary>Answer</summary>

**Security through obscurity + enumeration attacks:**

With sequential IDs:
- Attacker sees their payment ID is `12847`
- They can guess other payment IDs: `12846`, `12845`, etc.
- Even with auth checks, they learn how many payments exist
- Can brute-force to find valid IDs

With UUIDs like `a1b2c3d4-e5f6-7890-abcd-ef1234567890`:
- Impossible to guess other payment IDs
- No information leakage about total payments
- 128-bit randomness = practically unguessable

**Rule:** Use UUIDs for any sensitive/financial data exposed in URLs or APIs.

</details>

---

## Callbacks vs Webhooks

### Callback (Synchronous)

```
User clicks pay → Gateway page → User returns to your site
                                         │
                                         ▼
                              yoursite.com/payment/success?payment_id=xyz
```

```python
# views.py - Callback handler

def payment_callback(request):
    payment_id = request.GET.get('payment_id')

    # DANGER: This can be faked! User could manually visit this URL.
    # Only use for UI updates, not for confirming payment.

    return render(request, 'payment_pending.html', {
        'message': 'Payment is being verified...'
    })
```

**Problem:** User might close browser, or attacker could visit `/payment/success` directly.

---

### Webhook (Asynchronous)

```
Gateway confirms payment → Gateway POSTs to yoursite.com/webhook/
                                                    │
                                                    ▼
                                         Your server processes it
```

```python
# views.py - Webhook handler

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

@csrf_exempt  # Webhooks don't have CSRF tokens
def payment_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    # 1. Verify signature (CRITICAL!)
    if not verify_webhook_signature(request):
        return HttpResponse(status=401)

    # 2. Parse payload
    payload = json.loads(request.body)
    event_type = payload.get('event')

    # 3. Handle event
    if event_type == 'payment.completed':
        handle_payment_success(payload)
    elif event_type == 'payment.failed':
        handle_payment_failure(payload)

    # 4. Always return 200 (or gateway will retry!)
    return HttpResponse(status=200)
```

---

### 🔬 Hands-On: Test Webhooks Locally with ngrok

Let's receive a real webhook on your local Django server:

**Step 1: Start your Django server**
```bash
python manage.py runserver 8000
```

**Step 2: In another terminal, start ngrok**
```bash
# Install: brew install ngrok (Mac) or download from ngrok.com
ngrok http 8000
```

ngrok gives you a public URL like `https://abc123.ngrok.io`

**Step 3: Create a simple webhook view**
```python
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def test_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f"Received webhook: {data}")
        return JsonResponse({'status': 'received'})
    return JsonResponse({'error': 'POST only'}, status=405)

# urls.py
path('webhook/test/', views.test_webhook),
```

**Step 4: Simulate a payment gateway**
```bash
curl -X POST https://YOUR-NGROK-URL/webhook/test/ \
  -H "Content-Type: application/json" \
  -d '{"event": "payment.completed", "payment_id": "pay_123", "amount": 50000}'
```

Watch your Django terminal - you'll see the webhook data!

**Step 5: Use Stripe CLI for realistic testing**
```bash
# Install: brew install stripe/stripe-cli/stripe
stripe listen --forward-to localhost:8000/webhook/stripe/
stripe trigger payment_intent.succeeded
```

---

## Webhook Security: Signature Verification

**Why?** Anyone could POST to your webhook URL pretending to be Stripe/Razorpay.

**Solution:** Gateways sign webhooks with a secret. You verify the signature.

```python
# webhook_utils.py

import hmac
import hashlib

def verify_razorpay_signature(request, webhook_secret):
    """
    Razorpay sends signature in X-Razorpay-Signature header.
    """
    received_signature = request.headers.get('X-Razorpay-Signature', '')

    # Create expected signature
    payload = request.body
    expected_signature = hmac.new(
        key=webhook_secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    # Constant-time comparison (prevents timing attacks)
    return hmac.compare_digest(received_signature, expected_signature)


def verify_stripe_signature(request, webhook_secret):
    """
    Stripe sends signature in Stripe-Signature header.
    """
    import stripe

    payload = request.body
    sig_header = request.headers.get('Stripe-Signature', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        return True, event
    except stripe.error.SignatureVerificationError:
        return False, None
```

**Key points:**
- Use `hmac.compare_digest()` not `==` (prevents timing attacks)
- Store webhook secret in environment variables, never in code
- Log failed signature attempts for security monitoring

---

### 🧠 Security Quiz: Timing Attacks

**Question:** Why do we use `hmac.compare_digest(a, b)` instead of `a == b`?

```python
# Why not just this?
if received_signature == expected_signature:
    process_webhook()
```

<details>
<summary>Answer</summary>

**Timing attacks!**

Regular `==` comparison stops at the first different character:
- Comparing `"abcdef"` vs `"aXXXXX"` - fails fast (1 comparison)
- Comparing `"abcdef"` vs `"abcdeX"` - fails slow (5 comparisons)

An attacker can measure response times to guess the signature character by character!

`hmac.compare_digest()` takes **constant time** regardless of where strings differ. It always compares all characters, so timing reveals nothing.

**This is a real attack** - it's been used against GitHub, OAuth implementations, and many others.

</details>

---

### 🔬 Try It: Fake a Webhook (Then Block It)

**Challenge:** Try to send a fake webhook to your endpoint. Then fix your code to reject it.

```bash
# 1. This should work (no signature check yet)
curl -X POST http://localhost:8000/webhook/payment/ \
  -H "Content-Type: application/json" \
  -d '{"event": "payment.completed", "amount": 9999999}'

# 2. Add signature verification to your view

# 3. Now this should fail with 401:
curl -X POST http://localhost:8000/webhook/payment/ \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: fake_signature" \
  -d '{"event": "payment.completed", "amount": 9999999}'
```

---

## Idempotency: Handling Duplicate Webhooks

**Problem:** Gateways retry webhooks if they don't get a 200 response. You might process the same payment twice!

**Solution:** Track which events you've already processed.

```python
# models.py

class ProcessedWebhookEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True, db_index=True)
    event_type = models.CharField(max_length=100)
    processed_at = models.DateTimeField(auto_now_add=True)


# webhook handler

def handle_webhook(request):
    payload = json.loads(request.body)
    event_id = payload.get('event_id')  # Unique ID from gateway

    # Check if already processed
    if ProcessedWebhookEvent.objects.filter(event_id=event_id).exists():
        # Already handled - return 200 so gateway stops retrying
        return HttpResponse(status=200)

    # Process the event
    process_payment_event(payload)

    # Mark as processed
    ProcessedWebhookEvent.objects.create(
        event_id=event_id,
        event_type=payload.get('event')
    )

    return HttpResponse(status=200)
```

**Alternative:** Use database transactions with `select_for_update()` for race condition safety.

---

### 🧠 Race Condition Challenge

**Question:** Two webhook deliveries for the same event arrive at the exact same time (different server instances). Your idempotency check uses this code:

```python
if not ProcessedWebhookEvent.objects.filter(event_id=event_id).exists():
    process_payment(payload)
    ProcessedWebhookEvent.objects.create(event_id=event_id)
```

**What could go wrong?**

<details>
<summary>Answer</summary>

**Double processing!**

Timeline:
1. Server A: `exists()` → False (not found)
2. Server B: `exists()` → False (not found)  ← Both pass!
3. Server A: `process_payment()` → sends email, updates order
4. Server B: `process_payment()` → sends ANOTHER email, updates order again
5. Both try to create, one fails with unique constraint

**Fix:** Use `select_for_update()` or atomic get_or_create:

```python
from django.db import transaction

with transaction.atomic():
    event, created = ProcessedWebhookEvent.objects.select_for_update().get_or_create(
        event_id=event_id,
        defaults={'event_type': payload.get('event')}
    )
    if created:
        process_payment(payload)
```

This is covered more in **Class 13: Reconciliation**!

</details>

---

## Stripe Overview

Stripe is the most popular payment gateway globally.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **PaymentIntent** | Represents a payment attempt. Create one when user wants to pay. |
| **Checkout Session** | Hosted payment page. Stripe handles the UI. |
| **Customer** | Saved customer with payment methods for repeat purchases. |
| **Webhook Events** | `payment_intent.succeeded`, `payment_intent.payment_failed` |

### Typical Flow

```python
# 1. Create Checkout Session (server-side)
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
            'currency': 'inr',
            'unit_amount': 10000,  # ₹100.00 in paise
            'product_data': {'name': 'Order #123'},
        },
        'quantity': 1,
    }],
    mode='payment',
    success_url='https://yoursite.com/success',
    cancel_url='https://yoursite.com/cancel',
)

# 2. Redirect user to session.url

# 3. Handle webhook when payment completes
```

---

## Razorpay Overview

Razorpay is popular in India with UPI, cards, and netbanking support.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Order** | Create before payment. Contains amount and receipt info. |
| **Payment** | The actual payment against an order. |
| **Checkout** | JavaScript widget that handles payment UI. |
| **Webhook Events** | `payment.captured`, `payment.failed` |

### Typical Flow

```python
# 1. Create Order (server-side)
import razorpay

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

order = client.order.create({
    'amount': 10000,  # ₹100.00 in paise
    'currency': 'INR',
    'receipt': 'order_123',
})

# 2. Frontend uses order_id with Razorpay Checkout.js

# 3. Verify payment signature on callback
client.utility.verify_payment_signature({
    'razorpay_order_id': order_id,
    'razorpay_payment_id': payment_id,
    'razorpay_signature': signature
})

# 4. Handle webhook for async confirmation
```

---

## Common Patterns Across Gateways

| Pattern | Stripe | Razorpay | Why |
|---------|--------|----------|-----|
| Create intent first | PaymentIntent | Order | Prevents double-charging |
| Amount in smallest unit | Cents | Paise | Avoids floating point |
| Webhook verification | Stripe-Signature header | X-Razorpay-Signature | Security |
| Idempotency key | Built-in support | Manual | Retry safety |
| Test mode | `sk_test_*` keys | `rzp_test_*` keys | Safe development |

---

## Best Practices Checklist

- [ ] **Never trust callbacks alone** - Always verify via webhook
- [ ] **Verify webhook signatures** - Or anyone can fake payments
- [ ] **Handle idempotency** - Webhooks can arrive multiple times
- [ ] **Use UUID for payment IDs** - Don't expose sequential IDs
- [ ] **Store amounts in smallest unit** - Avoid floating point math
- [ ] **Log everything** - You'll need it for debugging and audits
- [ ] **Use test mode during development** - Real money is unforgiving
- [ ] **Handle all webhook events** - Not just success, but failures too
- [ ] **Return 200 quickly** - Do heavy processing async
- [ ] **Set up webhook retry monitoring** - Know when your endpoint is failing

---

## Common Pitfalls

### 1. Trusting the Callback URL
```python
# BAD - User can visit this URL directly!
def payment_success(request):
    order = Order.objects.get(id=request.GET['order_id'])
    order.status = 'paid'  # DANGER!
    order.save()
```

### 2. Not Handling Duplicate Webhooks
```python
# BAD - Will send 5 emails if webhook retries 5 times
def handle_payment_success(payload):
    send_confirmation_email(payload['email'])
```

### 3. Floating Point Amounts
```python
# BAD
amount = 10.50
# Might become 10.499999999999998

# GOOD
amount_paise = 1050  # Store as integer
```

### 4. Blocking Webhook Response
```python
# BAD - Gateway will timeout and retry
def webhook(request):
    process_payment()  # Takes 30 seconds
    send_email()
    update_inventory()
    return HttpResponse(200)

# GOOD - Return immediately, process async
def webhook(request):
    task_queue.enqueue(process_payment, payload)
    return HttpResponse(200)
```

---

## Quick Self-Test

1. Why can't you trust the callback URL alone?
2. What is HMAC and why is it used in webhooks?
3. What happens if your webhook returns 500?
4. Why store amounts in paise/cents instead of rupees/dollars?
5. What's the difference between a Stripe PaymentIntent and a Razorpay Order?

<details>
<summary>Answers</summary>

1. Users can close browser before redirect, or attackers can visit the URL directly
2. HMAC is Hash-based Message Authentication Code. It verifies the webhook came from the real gateway, not an attacker
3. The gateway will retry the webhook (potentially multiple times), which is why you need idempotency
4. Floating point numbers can have precision errors (10.50 might become 10.4999...). Integers are exact.
5. Both represent a "payment intent" - something created before actual payment to track the attempt. They serve the same purpose.

</details>

---

## 📚 Resources & Further Reading

### Official Documentation
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Razorpay Webhooks](https://razorpay.com/docs/webhooks/)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)

### Testing & Debugging Tools
| Tool | URL | Use Case |
|------|-----|----------|
| Webhook.site | https://webhook.site | See webhook payloads instantly |
| RequestBin | https://requestbin.com | Inspect HTTP requests |
| ngrok | https://ngrok.com | Expose localhost to internet |
| Stripe CLI | https://stripe.com/docs/stripe-cli | Test webhooks locally |
| Postman | https://postman.com | API testing |

### Test Credentials (Stripe)
```
Card Number: 4242 4242 4242 4242
Expiry: Any future date
CVV: Any 3 digits
```

### Test Credentials (Razorpay)
```
Card Number: 4111 1111 1111 1111
UPI: success@razorpay (for testing)
```

---

## 🎯 What's Next: Class 13 Preview

**Question to think about before next class:**

Your webhook processed successfully. You have:
- 1000 payments in your database marked "completed"
- 1000 payments in Razorpay's dashboard marked "captured"

**How do you verify they match?**

What if:
- A webhook was lost and your DB shows 999?
- A webhook was processed twice and your DB shows 1001?
- Amounts don't match due to a currency conversion bug?

This is **reconciliation** - ensuring your system matches the source of truth (the payment gateway). We'll cover:
- Daily reconciliation jobs
- Detecting discrepancies
- Handling edge cases (refunds, disputes, chargebacks)
- Cron jobs and scheduled tasks

---

*Class 12 - Payment Integration, Callbacks & Webhooks*
