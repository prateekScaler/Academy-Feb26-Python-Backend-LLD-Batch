# Design Expense Sharing (Splitwise)

- [Design Expense Sharing (Splitwise)](#design-expense-sharing-splitwise)
  - [Overview](#overview)
  - [Expectations](#expectations)
  - [Requirements gathering](#requirements-gathering)
  - [Requirements](#requirements)
  - [Use case diagrams](#use-case-diagrams)
  - [Class diagram](#class-diagram)
  - [API design](#api-design)

## Overview

Friends share expenses (equal/exact/percent), the app tracks who owes whom, and settles up with the fewest payments.

> **Difficulty:** Medium &nbsp;·&nbsp; **Key concepts:** Split strategies, balance settlement

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

  1. A user has a profile (name, phone) and can be in groups.
  2. An expense records who paid what and who owes what, with a description.
  3. Splits can be equal, exact, or by percentage; they must sum to the total.
  4. Track running balances (who owes whom).
  5. A user can view their total owed amount and history.
  6. Only a group's creator can add/remove members.
  7. Settle up: list the transactions to clear a user / a group.
  8. Good to have: minimise the number of settle-up transactions.
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
