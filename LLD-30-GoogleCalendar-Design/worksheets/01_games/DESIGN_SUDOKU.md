# Design Sudoku

- [Design Sudoku](#design-sudoku)
  - [Overview](#overview)
  - [Expectations](#expectations)
  - [Requirements gathering](#requirements-gathering)
  - [Requirements](#requirements)
  - [Use case diagrams](#use-case-diagrams)
  - [Class diagram](#class-diagram)
  - [API design](#api-design)

## Overview

A 9×9 grid puzzle: fill cells 1–9 so each row, column, and 3×3 box has no repeats; validate a board and optionally give hints.

> **Difficulty:** Medium &nbsp;·&nbsp; **Key concepts:** Grid validation, constraints, hints

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

  1. A 9×9 grid divided into nine 3×3 boxes.
  2. Some cells are pre-filled (givens) and cannot be changed.
  3. A player can place a digit 1–9 into an empty cell.
  4. Validate that no row, column, or box repeats a digit.
  5. Detect when the board is complete and correct.
  6. Optionally provide a hint (a valid digit for some cell).
  7. Support starting a new puzzle of a chosen difficulty.
  8. Reject an invalid placement with a clear reason.
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
