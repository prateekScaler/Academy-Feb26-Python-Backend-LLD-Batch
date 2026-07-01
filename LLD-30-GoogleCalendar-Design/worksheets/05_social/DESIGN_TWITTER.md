# Design Twitter

- [Design Twitter](#design-twitter)
  - [Overview](#overview)
  - [Expectations](#expectations)
  - [Requirements gathering](#requirements-gathering)
  - [Requirements](#requirements)
  - [Use case diagrams](#use-case-diagrams)
  - [Class diagram](#class-diagram)
  - [API design](#api-design)

## Overview

Users post tweets, follow others, and see a timeline of tweets from people they follow; feed generation is the core challenge.

> **Difficulty:** Hard &nbsp;·&nbsp; **Key concepts:** Tweet, follow, feed generation

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

  1. A user can post a tweet (text, optional media).
  2. A user can follow/unfollow other users.
  3. A user's home timeline shows recent tweets from people they follow.
  4. Support like and retweet.
  5. A user has a profile timeline of their own tweets.
  6. Feed is ordered by recency (and optionally rank).
  7. Handle high-follower 'celebrity' accounts (fan-out trade-off).
  8. Notifications for likes/follows/mentions.
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
