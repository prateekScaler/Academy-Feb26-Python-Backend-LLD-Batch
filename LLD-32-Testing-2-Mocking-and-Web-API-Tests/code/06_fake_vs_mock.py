"""
06 — Fake vs Mock: two kinds of double, two jobs
================================================

  * A MOCK verifies INTERACTIONS — "was save() called with this row?"
  * A FAKE is a real (but lightweight) IMPLEMENTATION — an in-memory
    stand-in you can actually store into and read back.

Rule of thumb: fake the things you STORE STATE in (repositories, caches);
mock the things you just POKE (email, SMS, analytics). Overusing mocks
couples tests to the implementation; a good fake tests behaviour.

Needs:  pip install pytest
"""

from unittest.mock import Mock
import pytest


class InMemoryUserRepo:
    """A FAKE repository — a real implementation backed by a dict."""
    def __init__(self):
        self._rows: dict[int, dict] = {}
    def save(self, user: dict) -> None:
        self._rows[user["id"]] = dict(user)
    def get(self, user_id: int) -> dict | None:
        return self._rows.get(user_id)


class SignupService:
    def __init__(self, repo, notifier):
        self.repo = repo
        self.notifier = notifier
    def register(self, user_id: int, email: str) -> None:
        self.repo.save({"id": user_id, "email": email, "status": "ACTIVE"})
        self.notifier.notify(email, "Welcome aboard!")


def test_fake_repo_lets_you_assert_real_stored_state():
    repo = InMemoryUserRepo()                    # FAKE — store & read back
    notifier = Mock()                            # MOCK — just poked
    SignupService(repo, notifier).register(7, "a@b.com")

    saved = repo.get(7)                          # behaviour, via the fake
    assert saved == {"id": 7, "email": "a@b.com", "status": "ACTIVE"}


def test_mock_notifier_verifies_the_interaction():
    repo, notifier = InMemoryUserRepo(), Mock()
    SignupService(repo, notifier).register(7, "a@b.com")
    notifier.notify.assert_called_once_with("a@b.com", "Welcome aboard!")


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
