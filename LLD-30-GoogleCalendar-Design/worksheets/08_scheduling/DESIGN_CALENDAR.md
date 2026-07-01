# Design Calendar

- [Design Calendar](#design-calendar)
  - [Overview](#overview)
  - [Expectations](#expectations)
  - [Requirements gathering](#requirements-gathering)
  - [Requirements](#requirements)
  - [Use case diagrams](#use-case-diagrams)
  - [Class diagram](#class-diagram)
  - [API design](#api-design)

## Overview

Users create events on calendars, invite attendees, set recurrence, and view their schedule across time zones; recurrence and free/busy are the stars.

> **Difficulty:** Hard &nbsp;·&nbsp; **Key concepts:** Recurring events, timezones, conflicts

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

  1. A user has one or more calendars; an event has a title, start, and end.
  2. An event can repeat by a rule (daily/weekly/monthly) until a date or N times.
  3. A single occurrence can be edited/deleted without changing the series (exception).
  4. Invite attendees who RSVP (accept/decline/tentative).
  5. View events by day/week/month.
  6. Detect conflicts (overlaps) and find a common free slot.
  7. Reminders N minutes before an event.
  8. Store times in UTC; display in the viewer's time zone (DST-aware).
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
