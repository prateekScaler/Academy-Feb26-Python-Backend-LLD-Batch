# Design Vending Machine

- [Design Vending Machine](#design-vending-machine)
  - [Overview](#overview)
  - [Expectations](#expectations)
  - [Requirements gathering](#requirements-gathering)
  - [Requirements](#requirements)
  - [Use case diagrams](#use-case-diagrams)
  - [Class diagram](#class-diagram)
  - [API design](#api-design)

## Overview

A machine dispenses products after the user selects one and inserts enough money, returning change; it's a classic state machine.

> **Difficulty:** Easy &nbsp;·&nbsp; **Key concepts:** State machine, inventory, change

## Expectations

* Code should be functionally correct.
* Code should be modular and readable — clean, professional-level code.
* Code should be extensible and scalable — accommodate new requirements with minimal changes.
* Code should follow good OOP design principles (SOLID, and the right design patterns).

## Requirements gathering

What questions would you ask to clarify scope before designing? Write yours first.

```


```

## Requirements

List ~8–10 functional requirements. Don't worry about getting them "right" — the skill is anticipating what the system needs. Write yours, then reveal the sample.

```


```

<details>
  <summary><strong>Click to see sample requirements</strong></summary>

  1. Products are stored in slots, each with a price and quantity.
  2. User selects a product, then inserts coins/notes.
  3. Dispense only when enough money is inserted and the slot is non-empty.
  4. Return change using available denominations.
  5. States: idle → item selected → money inserted → dispense → return change.
  6. Allow cancellation (refund inserted money).
  7. Reject if out of stock or insufficient change.
  8. Admin can refill inventory and collect cash.
</details>

## Use case diagrams

### Actors

Who are the actors (the roles that interact with the system)?

```


```

### Use cases

For each actor, list their interactions with the system.

#### Actor 1

Name of the actor — ` `

```
1. 
2. 
3. 
```

#### Actor 2

Name of the actor — ` `

```
1. 
2. 
3. 
```

*(Add more actors as needed.)*

**Draw the use-case diagram.**

```


```

## Class diagram

What are the major classes and their attributes?

```
Class name
  - attribute 1
  - attribute 2
```

List the cardinalities of the relationships between classes.

```


```

**Draw the class diagram** (mark composition ◆ / aggregation ◇, and the multiplicities).

```


```

## API design

Design an API for each use case. Format:

`name` — `HTTP METHOD` — `/url` — `?request body` — `?response body`

```


```
