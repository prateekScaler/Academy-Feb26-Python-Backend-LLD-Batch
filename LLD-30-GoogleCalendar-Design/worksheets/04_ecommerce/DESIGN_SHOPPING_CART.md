# Design Shopping Cart

- [Design Shopping Cart](#design-shopping-cart)
  - [Overview](#overview)
  - [Expectations](#expectations)
  - [Requirements gathering](#requirements-gathering)
  - [Requirements](#requirements)
  - [Use case diagrams](#use-case-diagrams)
  - [Class diagram](#class-diagram)
  - [API design](#api-design)

## Overview

Users browse a product catalog, add items to a cart, apply offers, and check out into an order; inventory must stay consistent.

> **Difficulty:** Medium &nbsp;·&nbsp; **Key concepts:** Cart operations, inventory, pricing

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

  1. Browse a catalog of products with price and stock.
  2. Add/remove/update item quantities in a cart.
  3. Cart subtotal updates with quantities and prices.
  4. Apply discounts/coupons (the open variable).
  5. Checkout creates an order and decrements inventory.
  6. Reject adding more than available stock.
  7. Support multiple payment methods.
  8. View order summary and status.
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
