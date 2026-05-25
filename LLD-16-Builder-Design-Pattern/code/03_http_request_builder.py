"""
03 - HTTP Request Builder (lots of optional knobs)
==================================================

An HTTP request has one required field (url) and many optional ones
(method, headers, body, timeout, retries...).
Builder lets every caller pay only for what they need.
"""

from dataclasses import dataclass, field


@dataclass
class HttpRequest:
    url: str
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    body: dict | None = None
    timeout: int = 30

    def execute(self):
        print(f"\n{self.method} {self.url}")
        if self.headers:
            for k, v in self.headers.items():
                print(f"  {k}: {v}")
        if self.body is not None:
            print(f"  body: {self.body}")
        print(f"  (timeout: {self.timeout}s)")


class HttpRequestBuilder:
    def __init__(self):
        self._url = None
        self._method = "GET"
        self._headers: dict = {}
        self._body = None
        self._timeout = 30

    def url(self, url):
        self._url = url
        return self

    def method(self, method):
        self._method = method.upper()
        return self

    def add_header(self, key, value):
        """Accumulates - call as many times as you have headers."""
        self._headers[key] = value
        return self

    def body(self, body):
        self._body = body
        return self

    def timeout(self, seconds):
        self._timeout = seconds
        return self

    def build(self) -> HttpRequest:
        if not self._url:
            raise ValueError("url required")
        # Defensive copy of headers
        return HttpRequest(
            url=self._url,
            method=self._method,
            headers=dict(self._headers),
            body=self._body,
            timeout=self._timeout,
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("--- Simple GET ---")
    simple = HttpRequestBuilder().url("https://api.example.com/users").build()
    simple.execute()

    print("\n--- Authenticated POST with body & longer timeout ---")
    create = (HttpRequestBuilder()
                .url("https://api.example.com/users")
                .method("POST")
                .add_header("Content-Type", "application/json")
                .add_header("Authorization", "Bearer xyz")
                .body({"name": "Alice", "email": "alice@example.com"})
                .timeout(60)
                .build())
    create.execute()

    print("\n--- Missing url raises early ---")
    try:
        HttpRequestBuilder().method("POST").build()
    except ValueError as e:
        print(f"ValueError: {e}")


if __name__ == "__main__":
    demo()
