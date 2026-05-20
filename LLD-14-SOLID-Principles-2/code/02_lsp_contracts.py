"""
The 4 contracts a subclass must honor (LSP).

Run each demo to see how a "legal" Python override can still break the
caller — that's exactly what LSP forbids.
"""

# ---------------------------------------------------------------
# 1. Preconditions cannot be STRENGTHENED
# ---------------------------------------------------------------
class User:
    def set_email(self, email):
        # Parent accepts any non-empty string
        if not email:
            raise ValueError("email required")
        self.email = email


class AdminUser(User):
    def set_email(self, email):
        # Child demands MORE: must end with @company.com
        # This is a tightened precondition - LSP violation
        if not email.endswith("@company.com"):
            raise ValueError("company email required")
        self.email = email


def register(u: User, email):
    u.set_email(email)


# ---------------------------------------------------------------
# 2. Postconditions cannot be WEAKENED
# ---------------------------------------------------------------
class UserRepo:
    def __init__(self, users):
        self._users = users

    def find_all(self):
        # Parent guarantees: returns a list sorted by name
        return sorted(self._users, key=lambda u: u["name"])


class FastUserRepo(UserRepo):
    def find_all(self):
        # Child guarantees LESS: returns unsorted
        return self._users


def first_user(repo: UserRepo):
    # Callers relied on alphabetical-first
    return repo.find_all()[0]


# ---------------------------------------------------------------
# 3. No NEW EXCEPTIONS the parent never promised
# ---------------------------------------------------------------
class PaymentError(Exception):
    pass


class CryptoNetworkError(Exception):
    pass


class PaymentGateway:
    def charge(self, amount):
        # Parent contract: throws PaymentError on bad input
        if amount < 0:
            raise PaymentError("invalid amount")
        return f"charged {amount}"


class CryptoGateway(PaymentGateway):
    def charge(self, amount):
        # Child throws a DIFFERENT exception type - LSP violation
        if amount < 0:
            raise CryptoNetworkError("bad amount")
        return f"crypto charged {amount}"


def process(gw: PaymentGateway, amt):
    try:
        return gw.charge(amt)
    except PaymentError:
        return "refunding..."


# ---------------------------------------------------------------
# 4. INVARIANTS must be preserved
# ---------------------------------------------------------------
class InsufficientFundsError(Exception):
    pass


class BankAccount:
    """Invariant: balance is never negative."""

    def __init__(self, balance=0):
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError()
        self.balance -= amount


class OverdraftAccount(BankAccount):
    def withdraw(self, amount):
        # Allows negative balance - INVARIANT BROKEN
        self.balance -= amount


def render_ui(acc: BankAccount):
    # UI used to assume balance >= 0
    assert acc.balance >= 0, "UI assumption broken"


if __name__ == "__main__":
    # 1. Preconditions
    try:
        register(AdminUser(), "alice@gmail.com")
    except ValueError as e:
        print("1. Precondition violated:", e)

    # 2. Postconditions
    users = [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}]
    print("2. UserRepo first:", first_user(UserRepo(users)))           # Alice
    print("   FastUserRepo first:", first_user(FastUserRepo(users)))   # Charlie (random)

    # 3. New exception type
    try:
        print("3. PaymentGateway:", process(PaymentGateway(), -5))     # "refunding..."
        print("   CryptoGateway:", process(CryptoGateway(), -5))       # CRASH
    except CryptoNetworkError as e:
        print("   uncaught CryptoNetworkError:", e)

    # 4. Invariant broken
    acc = OverdraftAccount(balance=10)
    acc.withdraw(50)
    print(f"4. balance now {acc.balance}")
    try:
        render_ui(acc)
    except AssertionError as e:
        print("   render_ui crashed:", e)
