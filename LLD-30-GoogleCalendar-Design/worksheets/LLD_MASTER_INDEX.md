# LLD Design Case Studies — Worksheets

A library of Low-Level Design case studies to practise the design playbook for interviews. Each **worksheet** is fill-in-the-blanks: write your own requirements, actors, class diagram, and APIs, then reveal the sample to check yourself. Each category has a **guide** with common entities, patterns, and pitfalls.

> Pair this with the interactive **[LLD interview-prep handbook](../LLD-interview-prep.html)** (machine-coding speed playbook, patterns & concepts quick-revise, conceptual Q&A).

## Category overview

| # | Category | Key focus | Case studies |
|---|---|---|---|
| 1 | [Board & Strategy Games](#1-board-strategy-games) | Game loop, turn management, move validation | Chess, Snake & Ladder, Sudoku |
| 2 | [Booking & Reservation Systems](#2-booking-reservation-systems) | Seat selection, concurrency, payment flow | Movie Ticket Booking, Hotel Reservation, Flight Booking |
| 3 | [Financial & Transaction Systems](#3-financial-transaction-systems) | State machines, transaction integrity | ATM, Expense Sharing (Splitwise), Digital Wallet |
| 4 | [E-commerce & Marketplace](#4-e-commerce-marketplace) | Catalog, cart, order lifecycle | Shopping Cart, Food Delivery |
| 5 | [Social & Communication](#5-social-communication) | Feed generation, messaging, notifications | Twitter, Chat / Messenger |
| 6 | [Content & Media Management](#6-content-media-management) | Catalog, search, access control | Library Management, File Storage / Drive |
| 7 | [Real-world Physical Systems](#7-real-world-physical-systems) | Resource allocation, state management | Parking Lot, Elevator, Vending Machine |
| 8 | [Scheduling & Calendar](#8-scheduling-calendar) | Recurring events, timezones, conflicts | Calendar, Meeting Scheduler |

---

## 1. Board & Strategy Games

**Guide:** [GUIDE_GAMES.md](./01_games/GUIDE_GAMES.md)

| Case study | Difficulty | Key concepts | Worksheet |
|---|---|---|---|
| Chess | Hard | Piece inheritance, move validation, check/checkmate | [DESIGN_CHESS.md](./01_games/DESIGN_CHESS.md) |
| Snake & Ladder | Easy | Random dice, board traversal, win condition | [DESIGN_SNAKE_LADDER.md](./01_games/DESIGN_SNAKE_LADDER.md) |
| Sudoku | Medium | Grid validation, constraints, hints | [DESIGN_SUDOKU.md](./01_games/DESIGN_SUDOKU.md) |

## 2. Booking & Reservation Systems

**Guide:** [GUIDE_BOOKING.md](./02_booking/GUIDE_BOOKING.md)

| Case study | Difficulty | Key concepts | Worksheet |
|---|---|---|---|
| Movie Ticket Booking | Medium | Seat locking, show management, concurrency | [DESIGN_MOVIE_BOOKING.md](./02_booking/DESIGN_MOVIE_BOOKING.md) |
| Hotel Reservation | Medium | Room types, date-range booking, availability | [DESIGN_HOTEL_BOOKING.md](./02_booking/DESIGN_HOTEL_BOOKING.md) |
| Flight Booking | Hard | Seat classes, passengers, PNR | [DESIGN_FLIGHT_BOOKING.md](./02_booking/DESIGN_FLIGHT_BOOKING.md) |

## 3. Financial & Transaction Systems

**Guide:** [GUIDE_FINANCIAL.md](./03_financial/GUIDE_FINANCIAL.md)

| Case study | Difficulty | Key concepts | Worksheet |
|---|---|---|---|
| ATM | Medium | State machine, card/PIN auth, cash dispensing | [DESIGN_ATM.md](./03_financial/DESIGN_ATM.md) |
| Expense Sharing (Splitwise) | Medium | Split strategies, balance settlement | [DESIGN_SPLITWISE.md](./03_financial/DESIGN_SPLITWISE.md) |
| Digital Wallet | Medium | Transaction types, balance management | [DESIGN_WALLET.md](./03_financial/DESIGN_WALLET.md) |

## 4. E-commerce & Marketplace

**Guide:** [GUIDE_ECOMMERCE.md](./04_ecommerce/GUIDE_ECOMMERCE.md)

| Case study | Difficulty | Key concepts | Worksheet |
|---|---|---|---|
| Shopping Cart | Medium | Cart operations, inventory, pricing | [DESIGN_SHOPPING_CART.md](./04_ecommerce/DESIGN_SHOPPING_CART.md) |
| Food Delivery | Hard | Restaurant, menu, order tracking, delivery | [DESIGN_FOOD_DELIVERY.md](./04_ecommerce/DESIGN_FOOD_DELIVERY.md) |

## 5. Social & Communication

**Guide:** [GUIDE_SOCIAL.md](./05_social/GUIDE_SOCIAL.md)

| Case study | Difficulty | Key concepts | Worksheet |
|---|---|---|---|
| Twitter | Hard | Tweet, follow, feed generation | [DESIGN_TWITTER.md](./05_social/DESIGN_TWITTER.md) |
| Chat / Messenger | Medium | Message types, conversation, delivery status | [DESIGN_MESSENGER.md](./05_social/DESIGN_MESSENGER.md) |

## 6. Content & Media Management

**Guide:** [GUIDE_CONTENT.md](./06_content/GUIDE_CONTENT.md)

| Case study | Difficulty | Key concepts | Worksheet |
|---|---|---|---|
| Library Management | Medium | Catalog, borrow/return, fines | [DESIGN_LIBRARY.md](./06_content/DESIGN_LIBRARY.md) |
| File Storage / Drive | Medium | Hierarchy, sharing, permissions | [DESIGN_FILE_STORAGE.md](./06_content/DESIGN_FILE_STORAGE.md) |

## 7. Real-world Physical Systems

**Guide:** [GUIDE_PHYSICAL.md](./07_physical/GUIDE_PHYSICAL.md)

| Case study | Difficulty | Key concepts | Worksheet |
|---|---|---|---|
| Parking Lot | Medium | Spot allocation, pricing, ticketing | [DESIGN_PARKING_LOT.md](./07_physical/DESIGN_PARKING_LOT.md) |
| Elevator | Medium | Request scheduling, direction, state | [DESIGN_ELEVATOR.md](./07_physical/DESIGN_ELEVATOR.md) |
| Vending Machine | Easy | State machine, inventory, change | [DESIGN_VENDING_MACHINE.md](./07_physical/DESIGN_VENDING_MACHINE.md) |

## 8. Scheduling & Calendar

**Guide:** [GUIDE_SCHEDULING.md](./08_scheduling/GUIDE_SCHEDULING.md)

| Case study | Difficulty | Key concepts | Worksheet |
|---|---|---|---|
| Calendar | Hard | Recurring events, timezones, conflicts | [DESIGN_CALENDAR.md](./08_scheduling/DESIGN_CALENDAR.md) |
| Meeting Scheduler | Medium | Free/busy, interval overlap, rooms | [DESIGN_MEETING_SCHEDULER.md](./08_scheduling/DESIGN_MEETING_SCHEDULER.md) |

---

## How to use a worksheet

1. Read the **Overview** and set a timer (~45 min for design, ~90 for machine coding).
2. Do **Requirements gathering** and **Requirements** *before* peeking — reveal only to compare.
3. Draw the **use-case** and **class diagrams**, then the **APIs**.
4. Check against the sample, note what you missed, and read the category **guide**.
