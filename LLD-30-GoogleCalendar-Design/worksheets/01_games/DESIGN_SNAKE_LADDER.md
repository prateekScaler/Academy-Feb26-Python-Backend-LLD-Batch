# Design Snake & Ladder

- [Design Snake & Ladder](#design-snake-ladder)
  - [Overview](#overview)
  - [Expectations](#expectations)
  - [Requirements gathering](#requirements-gathering)
  - [Requirements](#requirements)
  - [Use case diagrams](#use-case-diagrams)
  - [Class diagram](#class-diagram)
  - [API design](#api-design)

## Overview

A board game where players roll a die and move along a 1–100 board; snakes send you down, ladders send you up; first to 100 wins.

> **Difficulty:** Easy &nbsp;·&nbsp; **Key concepts:** Random dice, board traversal, win condition

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

  1. 2+ players take turns rolling a single die (1–6).
  2. A 100-cell board with a configurable set of snakes and ladders.
  3. Landing on a ladder bottom moves up; on a snake head moves down.
  4. Players move in turn order.
  5. The first player to reach exactly cell 100 wins.
  6. Number of players, snakes, and ladders are configurable at setup.
  7. A move that overshoots 100 is handled by a defined rule (stay / bounce).
  8. The system announces the winner and ends the game.
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
