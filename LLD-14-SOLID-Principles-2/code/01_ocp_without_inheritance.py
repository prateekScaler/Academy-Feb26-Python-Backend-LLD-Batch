"""
OCP without inheritance — 4 ways.

OCP says "open for extension, closed for modification". Inheritance + ABCs
is one way. It is not the only way.
"""

# ---------------------------------------------------------------
# 1. COMPOSITION — inject behavior as objects
# ---------------------------------------------------------------
class MinLengthValidator:
    def __init__(self, n):
        self.n = n

    def check(self, s):
        return len(s) >= self.n


class NoSpacesValidator:
    def check(self, s):
        return " " not in s


class HasDigitValidator:
    def check(self, s):
        return any(c.isdigit() for c in s)


class PasswordChecker:
    """Closed for modification. Open via the validators list."""

    def __init__(self, validators):
        self.validators = validators

    def is_valid(self, pw):
        return all(v.check(pw) for v in self.validators)


# Adding a new rule = new validator object. PasswordChecker is untouched.
checker = PasswordChecker([
    MinLengthValidator(8),
    NoSpacesValidator(),
    HasDigitValidator(),
])


# ---------------------------------------------------------------
# 2. CALLBACKS — first-class functions as the extension point
# ---------------------------------------------------------------
class EventBus:
    """The bus is closed for modification. Open via .on() subscriptions."""

    def __init__(self):
        self.handlers = []

    def on(self, fn):
        self.handlers.append(fn)

    def emit(self, event):
        for h in self.handlers:
            h(event)


bus = EventBus()
bus.on(lambda e: print("log:", e))
bus.on(lambda e: print("metric:", e))
# A new reaction = bus.on(...) - no EventBus edits.


# `sorted()` itself is OCP-in-the-stdlib via the `key=` callback:
people = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 22}]
sorted_by_age = sorted(people, key=lambda p: p["age"])
sorted_by_name = sorted(people, key=lambda p: p["name"])


# ---------------------------------------------------------------
# 3. PLUGINS / REGISTRY — collect handlers by name
# ---------------------------------------------------------------
EXPORTERS = {}


def register_exporter(name):
    def wrap(fn):
        EXPORTERS[name] = fn
        return fn
    return wrap


@register_exporter("pdf")
def _pdf(data):
    return f"<pdf>{data}</pdf>"


@register_exporter("csv")
def _csv(data):
    return ",".join(map(str, data))


def export(name, data):
    return EXPORTERS[name](data)


# Adding "json" exporter = new file with @register_exporter("json")
# No edit to export().


# ---------------------------------------------------------------
# 4. CONFIGURATION — a dict that maps inputs to behaviors
# ---------------------------------------------------------------
TAX_RULES = {
    "IN": lambda p: p * 0.18,
    "US": lambda p: p * 0.07,
    "GB": lambda p: p * 0.20,
}


def tax_for(country, price):
    return TAX_RULES[country](price)


# Adding Germany = one new entry in the dict. tax_for() never changes.
TAX_RULES["DE"] = lambda p: p * 0.19


if __name__ == "__main__":
    print("Composition:", checker.is_valid("hello123"))
    print("Callbacks:")
    bus.emit("user signed up")
    print("Plugin export PDF:", export("pdf", "hello"))
    print("Plugin export CSV:", export("csv", [1, 2, 3]))
    print("Config tax IN on 100:", tax_for("IN", 100))
    print("Config tax DE on 100:", tax_for("DE", 100))
