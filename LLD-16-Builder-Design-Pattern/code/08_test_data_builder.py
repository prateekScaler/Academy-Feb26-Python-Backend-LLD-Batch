"""
08 - Test Data Builder
======================

A SPECIAL real-world use of Builder you'll see in every mature codebase:
building test fixtures.

In tests you constantly need objects like User, Order, Article - mostly
with sensible defaults, and only one or two fields actually tweaked
per test. Without a Builder, every test gets cluttered with the same
boilerplate:

    user = User(id=1, name="Alice", email="alice@x.com", age=30,
                country="US", verified=True, premium=False, ...)

With a Builder that has GOOD defaults:

    user = a_user().build()                          # any user, defaults
    user = a_user().with_email("x@y.com").build()    # tweak just email
    user = a_user().unverified().build()              # named scenarios

The convention `a_user()` / `an_order()` (with the indefinite article)
reads naturally as English and is widely adopted in test codebases.
"""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str
    age: int
    country: str
    verified: bool
    premium: bool


class UserBuilder:
    """Defaults chosen so every test starts from a 'valid average user'."""

    def __init__(self):
        # Realistic defaults - so a test that doesn't care about a field
        # still gets sensible data without cluttering the test.
        self._id = 1
        self._name = "Test User"
        self._email = "test@example.com"
        self._age = 30
        self._country = "US"
        self._verified = True
        self._premium = False

    def with_id(self, uid):           self._id = uid;           return self
    def with_name(self, name):        self._name = name;        return self
    def with_email(self, email):      self._email = email;      return self
    def with_age(self, age):          self._age = age;          return self
    def from_country(self, country):  self._country = country;  return self

    # Named scenarios - read like English, document themselves
    def unverified(self):
        self._verified = False
        return self

    def premium(self):
        self._premium = True
        return self

    def minor(self):
        """Younger than 18 - useful for testing age-gating logic."""
        self._age = 16
        return self

    def build(self) -> User:
        return User(
            self._id, self._name, self._email, self._age,
            self._country, self._verified, self._premium,
        )


# Conventional factory alias - reads as "build a user"
def a_user() -> UserBuilder:
    return UserBuilder()


# ---------------------------------------------------------------------------
# Tests - notice how readable they become
# ---------------------------------------------------------------------------

def test_default_user_can_purchase():
    user = a_user().build()
    assert user.verified is True
    assert user.age >= 18
    print(f"test_default_user_can_purchase: PASS ({user.name})")


def test_unverified_user_cannot_purchase():
    user = a_user().unverified().build()
    assert user.verified is False
    # In real code: assert not purchase_service.can_buy(user)
    print(f"test_unverified_user_cannot_purchase: PASS (verified={user.verified})")


def test_minor_blocked_from_alcohol():
    user = a_user().minor().build()
    assert user.age < 18
    print(f"test_minor_blocked_from_alcohol: PASS (age={user.age})")


def test_premium_user_gets_discount():
    user = a_user().premium().build()
    assert user.premium is True
    print(f"test_premium_user_gets_discount: PASS (premium={user.premium})")


def test_eu_user_gets_gdpr_notice():
    user = a_user().from_country("DE").build()
    assert user.country == "DE"
    print(f"test_eu_user_gets_gdpr_notice: PASS (country={user.country})")


def test_combinations_compose_cleanly():
    user = a_user().premium().minor().from_country("IN").build()
    print(f"test_combinations_compose_cleanly: PASS ({user})")


if __name__ == "__main__":
    test_default_user_can_purchase()
    test_unverified_user_cannot_purchase()
    test_minor_blocked_from_alcohol()
    test_premium_user_gets_discount()
    test_eu_user_gets_gdpr_notice()
    test_combinations_compose_cleanly()

    print()
    print("Notice:")
    print("  - Each test reads like a sentence describing the scenario")
    print("  - No test contains irrelevant fields (no 'country=US' clutter")
    print("    in a test that's about age)")
    print("  - Adding a new field to User means updating ONE default,")
    print("    not every test in the codebase")
