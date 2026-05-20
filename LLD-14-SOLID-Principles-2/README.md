# LLD-14: SOLID Principles - Part 2

> Recap of OCP & LSP through questions, then a deep dive into ISP and DIP — the two principles that finish the framework.

---

## Today's Plan

1. **Revision** — OCP and LSP through questions
2. **The 4 ways to honor OCP without inheritance** — composition, callbacks, plugins, configuration
3. **The 4 contracts of LSP** — preconditions, postconditions, exceptions, invariants
4. **I — Interface Segregation Principle** — including: "Python has no `interface` keyword, so why does ISP apply?"
5. **D — Dependency Inversion Principle** — the principle that ties everything together
6. **LSP vs ISP** — they look similar; here's how they differ
7. **Practice** — Spot the violation (more scenarios)

---

## OCP — Quick Recap

> **Q:** What is the #1 sign that OCP is being violated?
<details><summary>Answer</summary>
A growing if/elif chain (or isinstance check) that gets longer every time a new type/variant is added. Each new feature forces an edit to an existing file.
</details>

> **Q:** "OCP means you must use inheritance everywhere." True or False?
<details><summary>Answer</summary>
False. OCP is about *abstraction*, not inheritance. You can achieve it with composition, callbacks, plugins, or configuration — see the 4 worked examples in `code/01_ocp_without_inheritance.py`.
</details>

> **Q:** "Make every class extensible, just in case." True or False?
<details><summary>Answer</summary>
False. Premature abstraction is its own anti-pattern. Apply OCP *where change is happening* — typically after the second or third edit to the same file.
</details>

---

## LSP — The 4 Contracts a Subclass Must Honor

1. **Preconditions** cannot be strengthened (child can't demand more from caller)
2. **Postconditions** cannot be weakened (child can't guarantee less)
3. **No new exceptions** (the LSP smoking gun)
4. **Invariants** must be preserved

See `code/02_lsp_contracts.py` for runnable examples of each violation.

---

## I — Interface Segregation Principle

> "No client should be forced to depend on methods it does not use."

### "Wait — Python doesn't have an `interface` keyword. Why does ISP apply?"

Because **"interface" here means the API surface a client depends on**, not the Java/C# language construct. In Python the same idea shows up as:

- An **abstract base class** (`abc.ABC`) with `@abstractmethod` methods
- A **`typing.Protocol`** (structural typing)
- A **plain class** used as a base/mixin
- Even a **duck-typed contract** that callers implicitly rely on

If any of those force a subclass to implement methods that don't belong to it (look for `pass`, `raise NotImplementedError`, or methods that just exist to satisfy the type), ISP is being violated. The keyword being absent doesn't make the smell go away.

### Signs of Violation
- Methods that just `pass` or `raise NotImplementedError`
- One ABC with many methods and clients that use only a subset
- Test setup keeps creating stubs for methods nothing under test calls

### How to Apply
1. List every client and the methods *that client* actually uses
2. Group methods by client role
3. Each group becomes its own small ABC / Protocol
4. A concrete class can implement multiple small interfaces

---

## D — Dependency Inversion Principle

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."

### The Direction Matters

```
BAD:  OrderService ──depends on──> MySQLDatabase  (concrete)
GOOD: OrderService ──depends on──> Database (ABC) <──implements── MySQLDatabase
```

Both high-level (`OrderService`) and low-level (`MySQLDatabase`) point *up* at the abstraction. Neither knows about the other directly.

### Signs of Violation
- `self.x = ConcreteThing()` inside `__init__`
- Importing concrete libraries (`psycopg2`, `sendgrid`) in business logic
- Hard-coded hosts, ports, API keys baked into a class
- Tests need real DBs/APIs because nothing can be mocked

### How to Apply
1. List every concrete dependency the class touches
2. Create an ABC/Protocol for each — named after the *role*, not the technology
3. Inject via constructor
4. Wire concrete implementations at the *composition root* (`main.py` / app factory)

---

## LSP vs ISP — Common Confusion

Both can be triggered by the same smell (`NotImplementedError` in a subclass), but they're different:

| | LSP | ISP |
|---|---|---|
| Cares about | Behavior of subclasses | Size of the interface |
| Asks | Can I substitute child for parent? | Is this client forced to depend on unused methods? |
| Direction of pain | Caller is surprised by child | Implementer is forced to write dead methods |
| Fix | Restructure hierarchy | Split the interface |

---

## Spot the Violation — More Scenarios

See `index.html` for 8+ new violation-spotting exercises beyond LLD-13.

---

## Code

- `code/01_ocp_without_inheritance.py` — 4 ways: composition, callback, plugin, config
- `code/02_lsp_contracts.py` — preconditions, postconditions, exceptions, invariants
- `code/03_isp_python.py` — ABC vs Protocol vs duck-typed ISP
- `code/04_dip_signup.py` — the signup flow worked example
- `code/05_lsp_vs_isp.py` — Penguin and printer dual-fix
