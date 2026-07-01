# Design Chat / Messenger

- [Design Chat / Messenger](#design-chat-messenger)
  - [Overview](#overview)
  - [Expectations](#expectations)
  - [Requirements gathering](#requirements-gathering)
  - [Requirements](#requirements)
  - [Use case diagrams](#use-case-diagrams)
  - [Class diagram](#class-diagram)
  - [API design](#api-design)

## Overview

Users exchange messages in 1:1 and group conversations, with delivery/read status and different message types.

> **Difficulty:** Medium &nbsp;·&nbsp; **Key concepts:** Message types, conversation, delivery status

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

  1. A user can send a message to another user (1:1).
  2. Support group conversations with many members.
  3. Messages have types (text, image, etc.).
  4. Track delivery and read status (sent/delivered/read).
  5. Show conversation history in order.
  6. Online/last-seen presence.
  7. Notifications for new messages.
  8. Good to have: typing indicators.
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
