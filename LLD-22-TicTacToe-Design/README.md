# LLD-22 — Tic-Tac-Toe Design (Part 1)

> First end-to-end LLD problem. **Design today, code next class (LLD-23).** Two halves: close the Pen exercise (requirements → five-step evolution → complete diagram), then run the 7-step playbook on Tic-Tac-Toe through Step 3 — every class derived from its requirement. **Drawing the class diagram is the homework** ([Discussion #12](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/12)); the diagram, APIs, patterns and code all happen live in LLD-23.

The interactive version (`index.html`) has a live pausable board, click-to-reveal requirement cards, and quizzes. This file is the same class as a succinct reference.

---

## Part 1 — Pen design: from requirements to the clean design

You submitted class diagrams in the GitHub discussion. The class walks the design through **five evolutions** — each step is forced by a requirement the previous design betrays.

### The functional requirements (R1–R9)

1. A pen is anything that can write.
2. Types of pens: Gel, Ball, Fountain, Marker, Throwaway.
3. Ball Pen and Gel Pen use a Refill (which has a tip/nib and an Ink) to write.
4. A Refill has a radius.
5. Ink has a colour.
6. Fountain pens have an Ink directly (no refill); their nib has a radius.
7. Each pen writes in its own way. Some pens write in the same way as others.
8. Every pen has a brand and a name.
9. Some pens are refillable; some are not (throwaway).

### The five evolutions — one mantra each

| Step | Driven by | Mantra | Fixes | Still broken / cost |
|---|---|---|---|---|
| **E1** one class + type enum + if-tree | all 9 at once, naively | "An if-tree on a type code is a class hierarchy waiting to be born." | — | SRP, OCP, nullable fields (R3 vs R6), if-tree (R7) |
| **E2** subclass per type | R2 + R7 | "Subclass for behaviour that varies — but a parent's promise binds EVERY child." | SRP, OCP | LSP: `change_refill()` on the base lies for Fountain/Throwaway (R9); `write()` duplicated (R7's 2nd half) |
| **E3** + WritingStrategy | R7 verbatim: *"some pens write in the same way as others"* | "Behaviour shared by SOME siblings moves out (composition), not up (inheritance)." | duplication | LSP still broken |
| **E4** Refillable / NonRefillable intermediates | R9 verbatim | "Put a method at the level of the tree where it is true for everyone below it." | LSP | capability welded to ONE tree axis — cross-cutting traits homeless |
| **E5** capability as `Protocol`, flat tree | R9 as a contract | "Model what a thing CAN DO as a contract; keep what it IS as a small tree." | LSP + ISP, all 9 honoured | conformance is implicit (mypy catches typos, not class definition) |

Cross-domain versions of the same mistakes: `Notification.send()` if-tree (E1), `Bird.fly()`/Penguin (E2), injected `RetryPolicy` vs a `RetryingGateway` base (E3), `ElectricBicycle` under `MotorisedVehicle` (E4), Python's own `Sized`/`Iterable` protocols (E5).

**Complete final shape:** `Pen` (abstract; brand, name, strategy) → five concrete pens; `WritingStrategy` (Smooth/Rough) injected; `RefillablePen` Protocol that Gel/Ball conform to and Fountain simply doesn't; `Refill ◆ Nib + ◆ Ink` (radius R4, colour R5). Runnable: [`code/01_pen_final_design.py`](code/01_pen_final_design.py).

---

## Part 2 — Tic-Tac-Toe design (Steps 1–3 of the playbook)

### Step 1 — Clarify

**Align first** (one line): *"Tic-Tac-Toe: 2 players on a 3×3 grid, alternate turns, a line of 3 wins — same page?"* Then the scope questions; each answer becomes a functional requirement:

1. Board — 3×3 only, or any N×N with win-on-K-in-a-row?
2. Players — exactly 2, or more later?
3. Can one player be a bot? With difficulty levels?
4. Different WAYS to win, or always K-in-a-row?
5. Output — CLI / web / API?

Feature suggestions worth offering (product sense, parked in future scope): timed moves, undo, spectators, analytics, tournaments.

### Step 2 — Functional requirements (complete sentences)

1. The game is played on an N×N board of cells. The classic version uses a 3×3 board.
2. Two players play the game, and each player is allotted a distinct symbol.
3. The players take turns alternately, and any player can make the first move.
4. A player can place their symbol only in an empty cell that is inside the board.
5. The first player to get K consecutive symbols in a row, a column, or a diagonal wins the game.
6. If the board becomes full and nobody has won, the game ends in a draw.
7. A player can be either a human or a bot, and every bot has a difficulty level.
8. After every move, the players can see the current state of the board.

**NFRs:** in-memory, single process/thread; N and K as constants in one place; new win rule = one new class; moves arrive via CLI (and the engine never knows that).

### Step 3 — Entities: every FR donates something

| Entity | Kind | From | One-line why |
|---|---|---|---|
| `Game` | class | FR-3/4/6 | Orchestrator: turn pointer (`(i+1) % len(players)`), flow validation, end-check |
| `Board` | class | FR-1 | Owns the N×N grid of Cells; place / cell / at / is_full / render |
| `Cell` | class | FR-1 + obstacle variant | **The flip:** vanilla TTT keeps it a value (`Symbol \| None`); "some cells start BLOCKED" adds a second fact → class with `is_empty()` / `can_place()` |
| `Player` | abstract class | FR-2 + FR-7 | name + symbol + the contract `choose_move(board)` — Game can't tell human from bot |
| `HumanPlayer` / `BotPlayer` | classes | FR-7 | Human parses input; Bot holds `difficulty: Difficulty` + a `MoveStrategy` |
| `MoveStrategy` / `Difficulty` | ABC + enum | FR-7 | Difficulty maps to a strategy object (RandomMove → MinimaxMove) — no if-else tree in the bot |
| `WinRule` / `KInARowRule(k)` | ABC + impl | FR-5 | The open variable — Strategy; K decoupled from N |
| `Symbol` | enum | FR-2 | Small named set; bool/str/int all fail (meaningless call sites, silent typos, magic numbers) |
| `GameStatus` | enum | FR-6 | Three real states; `is_over: bool` + nullable winner has a representable BUG state — the enum makes it unrepresentable |
| `InvalidMoveError` | exception | FR-4 | Rejection is part of the contract; a rejected move never flips the turn |
| `render()` | method | FR-8 | Presentation out of the mutation path |

**Ownership (the one lifetime question — "can the part outlive the whole or be shared?"):** Game ◆ Board (no → composition), Board ◆ Cell (no → composition), Game ◇ Player (yes, tournaments → aggregation), Game ◇ WinRule (stateless, shareable → aggregation), Player–Symbol (plain field).

### Where today stops — on purpose

You now have the full cast of classes, each traced to its requirement, plus the ownership answers. **Deferred to LLD-23** (after you've drawn the diagram yourself): the reference class diagram, the API signatures with "why not the alternative" reasoning, the edge-case table, and the patterns (WinRule + MoveStrategy Strategies, PlayerFactory, Memento-lite undo).

---

## Same framework, different game

The page walks each game's functional requirements through the exact same framework (align → FR sentences → circle nouns → three-way test → lifetime question), with each FR mapped to the Tic-Tac-Toe FR it echoes or diverges from:

- **Snake & Ladder** (~80% carries over): chance replaces choice — the turn FR becomes "roll a die and move forward", so no (row, col) input exists; board-triggered jumps (one `jumps` dict holds snakes AND ladders); landing rules vary by house → `MovementRule` Strategy; no draw exists, so `GameStatus` shrinks. The Cell test gives the *opposite* answer: a position has no second fact, so it stays an `int`. `Dice` is a class so tests can inject a `LoadedDice`. → [`DESIGN_SNAKE_AND_LADDER.md`](DESIGN_SNAKE_AND_LADDER.md)
- **Chess** (skeleton holds, two decisions FLIP): "sixteen pieces of six kinds, each moving by its own rule" flips the square's occupant into a `Piece` ABC hierarchy, and the one-WinRule idea multiplies into per-piece movement rules; endings multiply (check / checkmate / stalemate) so `GameStatus` GROWS; move history becomes a requirement — undo and notation fall out of the `Move` list. → [`DESIGN_CHESS.md`](DESIGN_CHESS.md)
- **Connect Four / Gomoku** (~95%): Gomoku is our FRs with two numbers changed (`Board(n=15)`, `KInARowRule(k=5)`); Connect Four changes one FR (pick a column, the disc falls) → one new method `Board.drop(col)`.

---

## Pre-work before LLD-23

1. **Draw the class diagram** from the classes we decided, and submit it to [Discussion #12](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/12) — arrows, diamonds (lifetime question!), multiplicities. We open LLD-23 by comparing submissions.
2. **Fill in the skeleton** — [`code/02_tictactoe_skeleton.py`](code/02_tictactoe_skeleton.py): Cell, Board, KInARowRule, Game bodies; the acceptance test at the bottom must pass. Stretch: N=5, K=5 → Gomoku.
3. **Think about — bots:** what does `RandomMove.choose()` do vs `MinimaxMove.choose()`? How does `Game` stay the same?
4. **Think about — undo:** where would `undo()` live — `Board` or `Game`? What must `make_move()` start recording, and why does a move list beat snapshotting the board every turn?

## Files

| File | What |
|---|---|
| [`index.html`](index.html) | Interactive class: live pausable board, click-to-reveal FR cards, evolution diagrams, quizzes |
| [`code/01_pen_final_design.py`](code/01_pen_final_design.py) | Resolved Pen design (E5) — runnable |
| [`code/02_tictactoe_skeleton.py`](code/02_tictactoe_skeleton.py) | Homework: Step-4 skeleton + acceptance test |
| [`DESIGN_SNAKE_AND_LADDER.md`](DESIGN_SNAKE_AND_LADDER.md) / [`DESIGN_CHESS.md`](DESIGN_CHESS.md) | Companion case studies |
