"""
LLD-38  |  Cloud-native patterns (adapted for Python)
=====================================================
DELIVERABLE 3 — EXTERNALIZED CONFIGURATION with pydantic-settings

THE RULE (from the 12-Factor App methodology): "Store config in the ENVIRONMENT."
--------------------------------------------------------------------------------
The SAME build of your app runs in dev, staging and prod. What changes between
them (database URL, timeouts, feature flags, secrets) must NOT be baked into the
code — it comes from OUTSIDE: environment variables and, for local dev, a `.env`
file. Benefits:

  * one artifact, many environments (no rebuild to change a URL),
  * secrets (API keys, DB passwords) never sit in the source tree / git history,
  * ops can retune timeouts without a code deploy.

pydantic-settings gives us this with TYPES and VALIDATION for free: declare the
shape of your config once, and it reads + parses + validates from env/.env.

PRECEDENCE (what wins when the same key is set in several places):

    real OS environment variable   >   .env file   >   field default in code

This file demonstrates all of that with a throwaway .env created at runtime, so
it runs out of the box with no setup.
"""

import os
import tempfile

from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# THE CONFIG SCHEMA. Each field is TYPED. pydantic-settings will look for a
# matching environment variable (case-insensitive) or a line in the .env file,
# parse the string into the declared type, and validate it.
# ---------------------------------------------------------------------------
class Settings(BaseSettings):
    # env_file tells it which .env to read; we override it per-instance below so
    # the demo can point at a throwaway file. `extra="ignore"` means unrelated
    # env vars won't crash us.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",
                                      extra="ignore")

    # A plain string WITH a default -> if nothing sets it, we fall back to this.
    service_name: str = "orders-service"

    # A required-ish string with a harmless default (real apps often have no
    # default here, forcing the value to come from the environment).
    db_url: str = "sqlite:///:memory:"

    # A FLOAT. The env/.env value arrives as the string "2.5"; pydantic parses
    # it to a real float. A non-numeric value will raise (see the validation demo).
    timeout_seconds: float = 3.0

    # A BOOL. pydantic understands "true"/"false"/"1"/"0"/"yes"/"no" etc.
    debug: bool = False

    # A SECRET. SecretStr keeps the value from being printed by accident
    # (repr shows '**********'); you must call .get_secret_value() to read it.
    # There is deliberately NO default: secrets must come from the environment.
    api_key: SecretStr = SecretStr("")


def source_of(field_name, dotenv_keys):
    """Explain WHERE a resolved value came from, following the precedence rule.
    (pydantic doesn't tell us directly, so we reconstruct it from what we know.)"""
    env_key = field_name.upper()
    if env_key in os.environ:
        return "OS env var  (highest precedence)"
    if env_key in dotenv_keys:
        return ".env file"
    return "field default (hard-coded in Settings)"


def show(settings, dotenv_keys, header):
    print(f"\n--- {header} ---")
    for field in ("service_name", "db_url", "timeout_seconds", "debug", "api_key"):
        value = getattr(settings, field)
        # Never print the raw secret; show a masked preview instead.
        if isinstance(value, SecretStr):
            raw = value.get_secret_value()
            shown = (raw[:6] + "…") if raw else "(empty)"
            shown = f"SecretStr('{shown}')"
        else:
            shown = repr(value)
        print(f"  {field:16} = {shown:34}  [type={type(getattr(settings, field)).__name__}, "
              f"from: {source_of(field, dotenv_keys)}]")


def demo():
    print("=" * 74)
    print("CONFIG DEMO  (pydantic-settings)   precedence: OS env > .env > default")
    print("=" * 74)

    # We build a throwaway .env in a temp dir so this runs anywhere and leaves
    # NOTHING behind in the repo. (In a real project the local .env lives next to
    # your code and is GITIGNORED — see .env.example for the committed template.)
    tmpdir = tempfile.mkdtemp(prefix="lld38-config-")
    env_path = os.path.join(tmpdir, ".env")
    dotenv_contents = (
        "# throwaway .env written by the demo\n"
        "DB_URL=postgres://app:s3cr3t@db.internal:5432/orders\n"
        "TIMEOUT_SECONDS=2.5\n"
        "DEBUG=true\n"
        "API_KEY=sk-live-DEMO-000111222333\n"
        # NOTE: SERVICE_NAME is intentionally ABSENT so you can see the default win.
    )
    with open(env_path, "w") as f:
        f.write(dotenv_contents)
    dotenv_keys = {"DB_URL", "TIMEOUT_SECONDS", "DEBUG", "API_KEY"}

    print(f"\nWrote throwaway .env at: {env_path}")
    print("Its contents:")
    for line in dotenv_contents.strip().splitlines():
        print(f"    {line}")

    # ----------------------------------------------------------------------
    # (a) READ FROM .env  +  (d) SECRET COMES FROM THE ENVIRONMENT
    #     Also shows (default win): SERVICE_NAME isn't in .env -> uses default.
    # ----------------------------------------------------------------------
    settings = Settings(_env_file=env_path)
    show(settings, dotenv_keys,
         "(a) Loaded from .env only  (service_name falls back to its DEFAULT)")
    print("    -> db_url/timeout/debug/api_key came from the .env file.")
    print("    -> service_name was NOT in .env, so the code default 'orders-service' won.")
    print("    -> api_key is a SecretStr: printing it can't leak the value.")

    # ----------------------------------------------------------------------
    # (b) OS ENV VAR OVERRIDES .env  (precedence: real env var beats .env)
    #     We set two real environment variables and reload.
    # ----------------------------------------------------------------------
    os.environ["SERVICE_NAME"] = "payments-prod"   # beats the code default
    os.environ["TIMEOUT_SECONDS"] = "0.25"         # beats the .env value 2.5
    settings2 = Settings(_env_file=env_path)
    show(settings2, dotenv_keys,
         "(b) After exporting real env vars SERVICE_NAME & TIMEOUT_SECONDS")
    print("    -> service_name is now 'payments-prod' (OS env beat the default).")
    print("    -> timeout_seconds is now 0.25 (OS env 0.25 beat the .env's 2.5).")
    print("    -> db_url/debug/api_key still come from .env (no OS override set).")

    # ----------------------------------------------------------------------
    # (c) TYPES ARE VALIDATED: a bad value RAISES instead of silently passing.
    # ----------------------------------------------------------------------
    print("\n--- (c) Validation: set TIMEOUT_SECONDS to a non-number ---")
    os.environ["TIMEOUT_SECONDS"] = "banana"
    try:
        Settings(_env_file=env_path)
        print("    (unexpected) no error raised")
    except ValidationError as e:
        # Show just the first error line so the point is obvious.
        first = e.errors()[0]
        print(f"    Settings(...) raised ValidationError as expected:")
        print(f"      field   : {first['loc']}")
        print(f"      problem : {first['msg']}")
        print(f"      input   : {first['input']!r}")
    finally:
        # tidy the process env back up so the demo is self-contained
        for k in ("SERVICE_NAME", "TIMEOUT_SECONDS"):
            os.environ.pop(k, None)

    # cleanup the throwaway file/dir
    os.remove(env_path)
    os.rmdir(tmpdir)

    print("\n" + "=" * 74)
    print("Takeaways: config is TYPED, VALIDATED, and comes from OUTSIDE the code.")
    print("Precedence is OS env  >  .env  >  default. Secrets live in the env,")
    print("never in source. Commit .env.example (placeholders); GITIGNORE the real")
    print(".env — it holds real secrets and must never reach version control.")
    print("=" * 74)


if __name__ == "__main__":
    demo()
