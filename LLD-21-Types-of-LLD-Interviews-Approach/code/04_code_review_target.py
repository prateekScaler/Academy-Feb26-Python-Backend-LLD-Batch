"""
LLD-21 · Example 04 — Code review interview target.

This file is DELIBERATELY full of smells. It's the kind of artifact an
interviewer might paste at the top of a code-review LLD round and ask:
"read it for 10 minutes, then walk me through what you'd change."

Don't read it as "good code". Read it as "find at least 10 things wrong,
prioritise them, propose a fix for the top 3."

The reviewer's notes are at the bottom — DO NOT scroll there until you've
listed your own findings.

Run:  python3 04_code_review_target.py  (yes, it runs — that's part of the trap)
"""

from __future__ import annotations
import time


# ============================================================================
# THE CODE THE CANDIDATE IS HANDED
# ============================================================================

class data:
    pass


users = {}
orders = []


def addUser(uid, n, e):
    u = data()
    u.uid = uid
    u.n = n
    u.e = e
    u.created = time.time()
    users[uid] = u


def placeOrder(uid, items, total):
    if uid in users:
        o = data()
        o.uid = uid
        o.items = items
        o.total = total
        o.status = "placed"
        orders.append(o)
        for i in items:
            if i == "phone":
                total = total + 50  # priority shipping
        # send email
        try:
            print(f"sending email to {users[uid].e} about order")
        except:
            pass
        # update analytics
        try:
            print(f"analytics: user {uid} spent {total}")
        except:
            pass
        return True
    else:
        return False


def getStatus(uid):
    s = []
    for o in orders:
        if o.uid == uid:
            s.append(o.status)
    return s


def cancelOrder(uid, idx):
    c = 0
    for o in orders:
        if o.uid == uid:
            if c == idx:
                o.status = "cancelled"
                return True
            c = c + 1
    return False


# ============================================================================
# CANDIDATE'S DEMO
# ============================================================================
def demo():
    addUser(1, "Ajit", "ajit@example.com")
    addUser(2, "Bhavna", "bhavna@example.com")
    placeOrder(1, ["phone", "case"], 30000)
    placeOrder(1, ["book"], 500)
    placeOrder(2, ["laptop"], 80000)
    print("status of user 1:", getStatus(1))
    cancelOrder(1, 1)
    print("status of user 1 after cancel:", getStatus(1))


if __name__ == "__main__":
    demo()


# ============================================================================
# REVIEWER'S NOTES — DO NOT READ UNTIL YOU'VE WRITTEN YOUR OWN LIST
# ============================================================================
#
# 1. Naming
#    - `data`, `addUser`, `placeOrder`, `n`, `e`, `s`, `c` — meaningless.
#      Code reads like an obfuscator's output. Fix: User dataclass,
#      OrderService.add_user(), descriptive names.
#
# 2. Global state
#    - `users = {}` and `orders = []` are module-level globals.
#      Impossible to test in isolation, impossible to have two services
#      in the same process. Fix: OrderService class holding state.
#
# 3. Stringly-typed status
#    - `o.status = "placed"`, `"cancelled"` — magic strings.
#      Misspell once, silent bug. Fix: OrderStatus enum.
#
# 4. Stringly-typed items
#    - `if i == "phone"` is the worst SOLID violation here. Adding any
#      new item type with priority shipping means editing this function.
#      Fix: Item class with .is_priority property, or a shipping Strategy.
#
# 5. Shipping logic mutates `total` AFTER total has been recorded
#    - Look at placeOrder line by line. The priority surcharge is added to
#      `total` AFTER `o.total = total` is set. The Order has the wrong
#      total stored. The analytics print uses the corrected one.
#      Fix: compute total ONCE, set it ONCE.
#
# 6. Side effects bundled into placeOrder
#    - placeOrder writes an order, sends an email, updates analytics.
#      SRP violation. Fix: emit an OrderPlaced event; observers handle
#      email + analytics independently (LLD-19 Observer).
#
# 7. Bare except: pass
#    - Hides every error: connection failure, auth failure, anything.
#      The classic "my email isn't sending and I can't tell why" bug.
#      Fix: catch specific exceptions, log them.
#
# 8. cancelOrder uses a per-user index
#    - `cancelOrder(uid, 1)` cancels the SECOND order placed by that user
#      in the order they appear in the global list. Race condition if
#      anyone adds an order between getStatus and cancelOrder.
#      Fix: stable order_id, cancelOrder(order_id).
#
# 9. getStatus returns a list of strings
#    - Caller can't tell which status belongs to which order. No order_id
#      in the response. Fix: list of (order_id, status) tuples or Order
#      objects.
#
# 10. No type hints, no docstrings
#    - Reviewer can't tell intent from signatures. Adding `: int`, `: str`,
#      and a one-line docstring would catch half the bugs above.
#
# WHAT TO SAY IN THE INTERVIEW
# ----------------------------------------------------------------------------
# Pick the TOP 3 and frame them as a refactor sequence:
#   1) Replace globals with an OrderService class       (enables tests)
#   2) Replace magic strings with OrderStatus enum      (kills silent bugs)
#   3) Extract Item.is_priority + ShippingStrategy      (kills the OCP smell)
#
# These three changes together transform the file's testability without
# rewriting it line-by-line. Mention 4–10 as "next round of cleanups".
# The interviewer wants to see PRIORITISATION, not exhaustiveness.
