"""
DIP — Signup flow worked example.

The same SignupService is shown twice:
- Before: hard-coded concrete dependencies (Postgres, SendGrid, file logger)
- After: depends on role-named abstractions, concrete wiring happens
  at the composition root (main / app factory)
"""

from abc import ABC, abstractmethod


# ===============================================================
# BEFORE — tight coupling
# ===============================================================
# (Pseudo-code; we don't actually want to import psycopg2 / sendgrid here.)
class SignupServiceBad:
    def __init__(self):
        # Concrete deps created right here in __init__
        self.db = self._connect_postgres()
        self.email = self._connect_sendgrid()
        self.logfile = open("signup.log", "a")

    def signup(self, user):
        self.db.execute("INSERT ...", user)
        self.email.send(user.email, "Welcome")
        self.logfile.write(f"signed up {user.id}\n")

    def _connect_postgres(self): ...   # stub
    def _connect_sendgrid(self): ...   # stub


# Problems:
# - Can't unit-test without real Postgres + SendGrid
# - Switching to Mailgun requires editing SignupService
# - The class "knows" it is using SQL


# ===============================================================
# AFTER — depend on abstractions
# ===============================================================

# Step 2: role-named abstractions (NOT technology-named)
class UserRepository(ABC):
    @abstractmethod
    def save(self, user): ...


class EmailSender(ABC):
    @abstractmethod
    def send(self, to, msg): ...


class Logger(ABC):
    @abstractmethod
    def info(self, msg): ...


# Step 3: high-level policy depends only on the abstractions
class SignupService:
    def __init__(self,
                 repo: UserRepository,
                 mail: EmailSender,
                 log:  Logger):
        self.repo = repo
        self.mail = mail
        self.log  = log

    def signup(self, user):
        self.repo.save(user)
        self.mail.send(user.email, "Welcome")
        self.log.info(f"signed up {user.id}")


# Low-level implementations - production
class PostgresUserRepo(UserRepository):
    def __init__(self, dsn): self.dsn = dsn
    def save(self, user):    print(f"[pg] saved {user.id}")


class SendGridSender(EmailSender):
    def __init__(self, key): self.key = key
    def send(self, to, msg): print(f"[sendgrid] {to}: {msg}")


class FileLogger(Logger):
    def __init__(self, path): self.path = path
    def info(self, msg):      print(f"[file:{self.path}] {msg}")


# Low-level implementations - test doubles
class FakeRepo(UserRepository):
    def __init__(self):           self.saved = []
    def save(self, user):         self.saved.append(user)


class InMemoryMailer(EmailSender):
    def __init__(self):           self.sent = []
    def send(self, to, msg):      self.sent.append((to, msg))
    def sent_count(self):         return len(self.sent)


class NullLogger(Logger):
    def info(self, msg): pass


# Step 4: composition root - the ONLY place that knows the concretes
def build_production_app():
    return SignupService(
        repo=PostgresUserRepo("postgres://..."),
        mail=SendGridSender("SG.KEY"),
        log =FileLogger("signup.log"),
    )


def build_test_app():
    return SignupService(
        repo=FakeRepo(),
        mail=InMemoryMailer(),
        log =NullLogger(),
    )


class User:
    def __init__(self, id, email):
        self.id, self.email = id, email


if __name__ == "__main__":
    print("--- production wiring ---")
    prod = build_production_app()
    prod.signup(User(1, "alice@example.com"))

    print("--- test wiring ---")
    svc = build_test_app()
    svc.signup(User(99, "test@example.com"))
    assert svc.mail.sent_count() == 1
    assert svc.repo.saved[0].id == 99
    print("tests passed")
