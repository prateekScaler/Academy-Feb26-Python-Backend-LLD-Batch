# Category Guide: Financial & Transaction Systems

## Overview

Financial & Transaction Systems LLD problems test **state machines, transaction integrity**. Work the [playbook](#the-lld-playbook-use-it-on-every-problem) below on each worksheet in this folder, then reveal the sample requirements to check yourself.

## Case studies in this category

| Case study | Difficulty | Key concepts |
|---|---|---|
| ATM | Medium | State machine, card/PIN auth, cash dispensing |
| Expense Sharing (Splitwise) | Medium | Split strategies, balance settlement |
| Digital Wallet | Medium | Transaction types, balance management |

## What interviewers look for here

* The right **entities & enums** for the domain, and an **association class** wherever a many-to-many carries data.
* The **open variable** modelled as a Strategy (so new variants don't touch working code).
* Clean **state management** where the domain is a state machine (status transitions guarded).
* **Edge cases** handled (empty / full / concurrent / invalid) and a **runnable demo**.

## The LLD playbook (use it on every problem)

1. **Clarify & scope** — list FRs out loud, cut scope, state assumptions.
2. **Entities & enums** — nouns → classes (`@dataclass`), fixed sets → `Enum`.
3. **Find the open variable** → a **Strategy** (pricing, split, movement, allocation…). New behaviour = new class (OCP).
4. **Layer it** — models / strategies / repositories / service. Keep models dumb, one orchestrator service.
5. **Demo** — a runnable `main()` with asserts that prints green.
6. **Trade-offs** — say the tensions out loud (concurrency, normalization, extensibility).

## Common pitfalls

* Coding before listing requirements; one **god class**; **magic strings** instead of enums.
* **Over-engineering** with patterns the problem doesn't need.
* No demo / it doesn't run; ignoring concurrency on shared mutable state.
