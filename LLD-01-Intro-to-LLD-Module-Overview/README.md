# LLD-01: Intro to Low-Level Design & Module Overview

> You've built a working Django backend — APIs, payments, caching. Now learn **how to write code that doesn't collapse under its own weight.**

---

## What is Low-Level Design (LLD)?

### HLD vs LLD — Two Different Zoom Levels

Think of building Zomato:

**HLD asks:** "What are the major pieces and how do they talk?"
- We need a User Service, Restaurant Service, Order Service, Payment Service
- Orders go into a message queue, Payment Service listens and processes
- We'll use PostgreSQL for orders, Redis for caching menus, S3 for images
- Draw the boxes, arrows, load balancers, databases

**LLD asks:** "Okay, now open the Order Service. How do you WRITE it?"
- What classes exist inside Order Service?
- How does `Order` relate to `OrderItem`? Is it inheritance or composition?
- When a new order type (subscription orders) is added, do you rewrite everything or just add a class?
- How do you handle 50 concurrent orders modifying the same restaurant's stock?

| | HLD | LLD |
|---|---|---|
| **Zoom Level** | Satellite view — entire city layout | Street view — inside one building |
| **Question** | "How many services? What database? What queue?" | "What classes? What methods? What patterns?" |
| **Output** | Architecture diagram with boxes and arrows | Class diagrams, code structure, interfaces |
| **Failure looks like** | System can't scale, services can't communicate | Code is a mess, every change breaks 5 things |
| **Interview example** | "Design the architecture of WhatsApp" | "Design the class structure of a parking lot system" |
| **Who does it** | Senior engineers / architects | Every developer, every day |

**Key insight:** You can have a perfect HLD (microservices, Kafka, Redis) but if the code INSIDE each service is poorly structured, the project still fails. LLD is about the code you write every day.

---

## Why Does LLD Matter? The Four Qualities of Good Code

Code that "works" is not enough. Code must be **readable, reusable, extensible, and maintainable.** These aren't buzzwords — they are the difference between code that survives and code that gets rewritten.

### 1. Readability — "Can someone else understand this?"

**Bad:**
```python
def p(d, t):
    r = 0
    for i in d:
        if i['t'] == t:
            r += i['a'] * (1 - i['d']/100)
    return r
```

**Good:**
```python
def calculate_total_for_category(dishes, category):
    total = 0
    for dish in dishes:
        if dish['category'] == category:
            discounted_price = dish['price'] * (1 - dish['discount'] / 100)
            total += discounted_price
    return total
```

Same logic. One takes 30 seconds to understand, the other takes 5. Multiply that across a codebase and a team.

> **Question:** You join a team. The codebase has 200 functions like the "bad" example. You need to fix a billing bug. Estimate how long it takes vs if the code looked like the "good" example. What's the real cost of unreadable code?

---

### 2. Reusability — "Can I use this in more than one place?"

**Bad:**
```python
def send_order_email(order):
    subject = f"Order #{order.id} confirmed"
    body = f"Your order of {order.total} is confirmed"
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login('admin@restaurant.com', 'password123')
    smtp.sendmail('admin@restaurant.com', order.customer.email, 
                  f"Subject: {subject}\n\n{body}")
    smtp.quit()

def send_welcome_email(user):
    subject = "Welcome!"
    body = f"Welcome {user.name}!"
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login('admin@restaurant.com', 'password123')
    smtp.sendmail('admin@restaurant.com', user.email, 
                  f"Subject: {subject}\n\n{body}")
    smtp.quit()
```

The SMTP connection logic is copy-pasted. If you switch from Gmail to SendGrid, you change it in 2 (or 20) places.

**Good:**
```python
def send_email(to_email, subject, body):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login('admin@restaurant.com', 'password123')
    smtp.sendmail('admin@restaurant.com', to_email, 
                  f"Subject: {subject}\n\n{body}")
    smtp.quit()

def send_order_email(order):
    send_email(order.customer.email, 
               f"Order #{order.id} confirmed",
               f"Your order of {order.total} is confirmed")

def send_welcome_email(user):
    send_email(user.email, "Welcome!", f"Welcome {user.name}!")
```

Switch to SendGrid? Change ONE function.

> **Question:** Your restaurant app sends emails for: order confirmation, order cancellation, welcome, password reset, daily report to owner. With the "bad" approach, how many places do you change when switching email providers? What bugs might you introduce?

---

### 3. Extensibility — "Can I add new features without rewriting?"

**Bad:**
```python
def calculate_delivery_fee(city):
    if city == "Mumbai":
        return 40
    elif city == "Delhi":
        return 35
    elif city == "Bangalore":
        return 45
    # Every new city = modify this function
```

**Good:**
```python
DELIVERY_FEES = {
    "Mumbai": 40,
    "Delhi": 35,
    "Bangalore": 45,
}

def calculate_delivery_fee(city):
    if city not in DELIVERY_FEES:
        raise ValueError(f"Delivery not available in {city}")
    return DELIVERY_FEES[city]
```

Adding a new city is adding one line to a dictionary, not touching the function logic.

> **Question:** Your PM says "we're launching in 50 new cities next month." With the if/elif approach, what happens to code review, testing, and the risk of breaking an existing city's fee? How does the data-driven approach change that?

---

### 4. Maintainability — "Can I change this without breaking everything?"

**Bad:**
```python
def place_order(user_id, dish_ids):
    # Step 1: Validate user
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    if not user: return "User not found"
    
    # Step 2: Calculate total
    total = 0
    for did in dish_ids:
        dish = db.query(f"SELECT * FROM dishes WHERE id = {did}")
        total += dish['price']
    
    # Step 3: Apply discount
    if user['is_premium']:
        total *= 0.9
    
    # Step 4: Charge payment
    razorpay.charge(user['card'], total)
    
    # Step 5: Create order in DB
    db.query(f"INSERT INTO orders ...")
    
    # Step 6: Send email
    smtp = smtplib.SMTP(...)
    smtp.sendmail(...)
    
    # Step 7: Send SMS
    twilio.send(...)
    
    return "Order placed"
```

One function doing 7 things. Change the discount logic? You're editing a 60-line function that also handles payments, emails, and SMS. One typo and orders stop working entirely.

**Good:**
```python
def place_order(user_id, dish_ids):
    user = get_user(user_id)
    dishes = get_dishes(dish_ids)
    total = calculate_total(dishes, user)
    charge_payment(user, total)
    order = create_order(user, dishes, total)
    notify_customer(user, order)
    return order
```

Each function has ONE job. Change discount logic? Edit `calculate_total`. Switch from Razorpay to Stripe? Edit `charge_payment`. Nothing else is affected.

> **Question:** A bug report says "premium users are being charged full price." In the bad code, where do you look? How long does it take to find line 3 of a 60-line function vs finding the `calculate_total` function? What if fixing the discount accidentally broke the email sending?

---

## LLD Interview Types

LLD interviews come in two distinct formats. You need to prepare differently for each.

### Machine Coding Round

**What it is:** You're given a problem and 60-90 minutes to write **working code** on your laptop/IDE.

**What they judge:**
- Does the code compile and run?
- Are the classes well-structured?
- Is it extensible? (they often add a twist at the 45-minute mark)
- Code quality — naming, separation of concerns, no god classes

**Example:** "Build a splitwise-like expense sharing app. Support equal splits. You have 90 minutes."
Then at 45 min: "Now add percentage-based splits too."

**How to prepare:** Practice building full working systems under time pressure. Think about your class structure BEFORE you start typing.

### Design Discussion Round

**What it is:** A whiteboard/doc conversation. You discuss classes, relationships, and trade-offs. You may write pseudocode but the focus is on DESIGN, not running code.

**What they judge:**
- Can you identify the right entities/classes?
- Do you understand relationships (inheritance vs composition)?
- Can you apply design patterns where appropriate?
- Can you explain trade-offs?
- Do you handle edge cases in your design?

**Example:** "Design a parking lot system. Walk me through your classes."

**How to prepare:** Practice drawing class diagrams, explaining WHY you chose a particular pattern, and thinking about extensibility upfront.

| | Machine Coding | Design Discussion |
|---|---|---|
| **Time** | 60-90 minutes | 45-60 minutes |
| **Output** | Working code | Class diagram + discussion |
| **Tools** | Your laptop / IDE | Whiteboard / Google Doc |
| **Focus** | Does it work + is it clean? | Is the design sound? |
| **Twist** | "Now add this feature" (tests extensibility) | "What if we need to support X?" |
| **Common at** | Flipkart, Uber, Swiggy, PhonePe | Google, Amazon, Microsoft |

---

## This LLD Module — Structure & Roadmap

This module has **3 parts** that build on each other. Here's what we cover and why each topic matters.

### Module 1: Foundations (OOP + Concurrency + Python Advanced)

```
OOP (3 classes)
├── OOP-1: Intro to OOP, Access Modifiers, Constructors
├── OOP-2: Inheritance and Polymorphism
└── OOP-3: Static Methods and Abstract Base Classes

Concurrency (4 classes)
├── Concurrency-1: Introduction to Processes and Threads
├── Concurrency-2: Executors and Futures
├── Concurrency-3: Semaphores and Deadlocks
└── Concurrency-4: Asynchronous I/O

Python Advanced (4 classes)
├── Advanced-1: Typing and Generics
├── Advanced-2: Collections
├── Advanced-3: Lambda Functions and Functional Programming
└── Advanced-4: Exception Handling and Miscellaneous
```

**Why this comes first:** You can't write good design patterns without understanding OOP. You can't design thread-safe systems without understanding concurrency. You can't write production Python without knowing types, collections, and error handling. These are the building blocks everything else depends on.

### Module 2: Design Principles & Patterns

```
├── SOLID Principles
├── Intro to Design Patterns + Singleton
├── Builder Pattern
├── Factory + Prototype Patterns
├── Adapter + Strategy Patterns
├── Observer + Decorator Patterns
├── UML Diagrams
└── Types of LLD Interviews + How to Approach LLD Problems
```

**Why this comes second:** SOLID principles tell you WHAT good code looks like. Design patterns give you PROVEN SOLUTIONS to common problems. You need OOP fundamentals first — patterns like Strategy use polymorphism, Observer uses interfaces, Decorator uses inheritance. Without Module 1, these patterns are just memorized recipes instead of deeply understood tools.

**Key connections:**
- **SOLID** builds directly on OOP — Single Responsibility, Open/Closed, Liskov Substitution all require understanding classes and inheritance
- **Strategy Pattern** = polymorphism in action (OOP-2)
- **Observer Pattern** = interfaces + decoupling (OOP-3)
- **Decorator Pattern** = inheritance + composition (OOP-2, OOP-3)
- **Factory Pattern** = abstract classes + constructors (OOP-1, OOP-3)
- **Thread-safe Singleton** = concurrency + patterns (Concurrency-1, Concurrency-3)

### Module 3: Case Studies — Design & Code

```
├── Design TicTacToe → Code TicTacToe
├── Design Parking Lot → Code Parking Lot
├── Design BookMyShow → Code BookMyShow
├── Design Splitwise → Code Splitwise
└── Design Google Calendar
```

**Why this comes last:** This is where everything comes together. Each case study requires you to:
1. Identify entities and relationships (OOP)
2. Apply SOLID principles and design patterns (Module 2)
3. Handle concurrency (what if two users book the same seat?)
4. Write production-quality Python (types, exceptions, collections)

**Key connections:**
- **Parking Lot** — Strategy (pricing), Factory (vehicle types), Observer (spot availability notifications)
- **BookMyShow** — Concurrency is critical (two users booking the same seat), Strategy (different pricing tiers)
- **Splitwise** — Observer (notify users of new expenses), Strategy (equal/exact/percentage splits)
- **Google Calendar** — Observer (event reminders), Builder (complex event creation)

### How It All Links Together

```
Module 1: Foundations          Module 2: Patterns           Module 3: Case Studies
─────────────────────          ──────────────────           ──────────────────────
OOP (classes, inheritance) ──→ SOLID, Strategy, Factory ──→ Parking Lot, BookMyShow
Concurrency (threads, locks)─→ Thread-safe Singleton   ──→ BookMyShow (seat booking)
Advanced Python (types) ─────→ UML Diagrams             ──→ All case studies
```

> **Question:** If you skip Module 1 and jump straight to Design Patterns, what happens when someone asks you "why did you use the Strategy pattern here?" and you can't explain polymorphism? What happens in the BookMyShow case study when two users try to book the same seat and you don't understand thread safety?

---

## Resources

### Python Refresher
- [Scaler Python Topics](https://www.scaler.com/topics/python/) — Revise core Python concepts (data types, loops, functions, OOP basics)

### LLD Practice
- [awesome-low-level-design](https://github.com/ashishps1/awesome-low-level-design) — 30+ LLD problems (Parking Lot, BookMyShow, Splitwise) with solutions in multiple languages. Pick one, set a 90-minute timer, build from scratch.
- [Refactoring Guru — Design Patterns](https://refactoring.guru/design-patterns/python) — Best visual reference for all design patterns with Python examples. Bookmark this for Module 2.

### OOP & Concurrency
- [Python OOP Tutorial — Corey Schafer (YouTube)](https://www.youtube.com/watch?v=ZDa-Z5JzLYM&list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc) — 6-part series covering classes, inheritance, decorators, special methods
- [Concurrency in Python — Real Python](https://realpython.com/python-concurrency/) — Threading, multiprocessing, asyncio with practical examples
- [SOLID Principles — Real Python](https://realpython.com/solid-principles-python/) — Deep dive into each principle with before/after Python code
