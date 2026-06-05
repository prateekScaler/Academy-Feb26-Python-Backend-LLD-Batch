"""
LLD-20 · Decorator · Example 5 — Django/FastAPI middleware as Decorator.

Run:  python3 05_django_middleware_pattern.py

Every modern web framework's middleware system IS the Decorator
pattern at the HTTP-request level. This file builds a tiny middleware
chain from scratch so you can see what Django/FastAPI/Express do
under the hood.

Component:        a "handler" — takes a Request, returns a Response
ConcreteComponent: the actual view function (handles business logic)
Decorator:        a middleware wrapping a handler
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Protocol


# ====================================================================
# Domain types
# ====================================================================
@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str]
    body: bytes = b""


@dataclass
class Response:
    status: int
    body: str
    headers: dict[str, str]


# Handler = a Component. Just a callable.
Handler = Callable[[Request], Response]


# ====================================================================
# The "view" — ConcreteComponent
# ====================================================================
def view_handler(req: Request) -> Response:
    """The actual application logic."""
    if req.path == "/hello":
        return Response(200, f"hello from {req.path}", {})
    return Response(404, "not found", {})


# ====================================================================
# Middleware (Decorators) — each wraps a handler and returns a handler
# ====================================================================
def auth_middleware(next_handler: Handler) -> Handler:
    def wrapper(req: Request) -> Response:
        if "Authorization" not in req.headers:
            return Response(401, "unauthorised", {})
        print(f"  [auth] OK  ({req.headers['Authorization']})")
        return next_handler(req)
    return wrapper


def logging_middleware(next_handler: Handler) -> Handler:
    def wrapper(req: Request) -> Response:
        print(f"  [log] → {req.method} {req.path}")
        resp = next_handler(req)
        print(f"  [log] ← {resp.status}  body={resp.body[:50]!r}")
        return resp
    return wrapper


def timing_middleware(next_handler: Handler) -> Handler:
    def wrapper(req: Request) -> Response:
        import time
        t0 = time.perf_counter()
        resp = next_handler(req)
        ms = (time.perf_counter() - t0) * 1000
        resp.headers["X-Response-Time-ms"] = f"{ms:.2f}"
        print(f"  [timing] {ms:.3f} ms")
        return resp
    return wrapper


def cors_middleware(next_handler: Handler, *, allow_origin: str = "*") -> Handler:
    """Middleware with parameters — wraps in an extra layer."""
    def wrapper(req: Request) -> Response:
        resp = next_handler(req)
        resp.headers["Access-Control-Allow-Origin"] = allow_origin
        return resp
    return wrapper


# ====================================================================
# Build the chain the way Django does — outermost first
# ====================================================================
def build_app() -> Handler:
    """Like Django's settings.MIDDLEWARE = [...]."""
    app: Handler = view_handler

    # Apply in REVERSE so the FIRST in the list is the OUTERMOST wrapper
    middleware_list_outer_to_inner = [
        logging_middleware,
        timing_middleware,
        cors_middleware,
        auth_middleware,
    ]
    for middleware in reversed(middleware_list_outer_to_inner):
        app = middleware(app)

    return app


# ====================================================================
# Demo
# ====================================================================
def main() -> None:
    app = build_app()

    print("--- 1. Request without auth ---")
    req1 = Request(method="GET", path="/hello", headers={})
    resp1 = app(req1)
    print(f"  → {resp1.status} {resp1.body}  headers={resp1.headers}")

    print("\n--- 2. Request with auth ---")
    req2 = Request(method="GET", path="/hello",
                   headers={"Authorization": "Bearer abc-123"})
    resp2 = app(req2)
    print(f"  → {resp2.status} {resp2.body}  headers={resp2.headers}")

    print("\n--- 3. Unknown path with auth ---")
    req3 = Request(method="GET", path="/nope",
                   headers={"Authorization": "Bearer abc-123"})
    resp3 = app(req3)
    print(f"  → {resp3.status} {resp3.body}")

    print("\nWhat Django/FastAPI do is exactly this — Decorator pattern at HTTP scale.")


if __name__ == "__main__":
    main()
