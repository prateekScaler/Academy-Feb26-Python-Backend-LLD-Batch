# LLD-23 — Tic-Tac-Toe: Code (Part 2)

> Steps 4–7 of the playbook. From [LLD-22's diagrams](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/tree/main/LLD-22-TicTacToe-Design) to a running game: reference class diagram → APIs → live build → demo → trade-offs. **Everything from LLD-22's design pays off in code.**

**Quick start:**
- `python3 code/01_tictactoe.py` — all FRs asserted green
- `python3 code/01_tictactoe.py play` — two-player CLI
- `cd code/tictactoe && python3 main.py` — file-by-file package build
- Open `index.html` in a browser for the interactive page with diagrams, quizzes, and code walkthroughs

---

## Step 1 — Relationships: re-derive every line before you see it drawn

From LLD-22, the one question that decides every diamond: *"can the part outlive the whole — or be shared?"*

- **Game ◆ Board · Board ◆ Cell** — Composition (filled diamond). Can this board exist after its game ends? Can a cell move to another board? No, twice → composition chain. Cells never leave their board; one fact today (`symbol`) — the final design keeps the tiny class anyway, so tomorrow's facts have a home.
- **Game ◇ Player** — Aggregation (open diamond). When this game ends, do Ajit and Vipul stop existing? They outlive it → the game *borrows* two players; a tournament hands the same objects to the next game. Multiplicity: has 2. ⚠️ Most common submission mistake: a filled diamond here — it welds a player's lifetime to one game; tournaments become impossible.
- **Game ◇ WinRule · BotPlayer ◇ MoveStrategy** — Aggregation (open diamond), for the *other* reason: stateless & shareable. One `KInARowRule()` can judge every game in the building. MoveStrategy is injected at construction, chosen by `Difficulty`, swappable without touching `BotPlayer`.
- **HumanPlayer / BotPlayer → Player · KInARowRule → WinRule** — Inheritance / realisation. Is-a → the hollow triangle, always pointing at the parent. Solid line = inherits a class; dashed line = implements an abstract contract (realisation). No diamonds on these lines, ever — inheritance is not ownership.
- **Game → GameStatus · Player — Symbol** — Dependency / attribute. `status()` *returns* an enum value: a dashed dependency arrow ("uses / returns"), the weakest line in UML. Symbol is a plain attribute — enums, strings, and numbers ride along as fields; ownership arrows on them is diagram noise.

## Step 2 — The reference class diagram (classes + relationships only)

Deliberately **no methods yet** — behaviours get derived from the FRs next.

Read it top-down:
- **Game ◆ Board ◆ Cell** — the composition chain: created together, die together
- **Game ◇ Player (2) · Game ◇ WinRule** — borrowed: both outlive the game
- **Game ⇢ GameStatus** — returned, not owned
- **Player** is an abstract contract — `HumanPlayer` prompts, `BotPlayer` picks through its `MoveStrategy`; Game can't tell them apart
- **KInARowRule ⇢▷ WinRule** — the dashed triangle is the plug-in socket for Connect-Four / Gomoku

## Step 3 — Behaviours from the FRs: every FR donates a method

Same derivation as the entities, second pass. Re-read each FR as a *verb*, and the question is always the same: **whose job is it?**

**Warm-up — "where does `make_move()` live?"** → On **Game** — it coordinates turns + win check. `make_move()` does FOUR things: validate, mutate the board, switch turn, check win/draw. Three of those are coordination — that's the Game's job. Board only knows about grid cells; it should expose `place(r, c, sym)` and `is_full()`, not the whole turn dance.

- **FR-1** — *"an N×N board of cells"*
  - **Board** — geometry + occupancy: `place(row, col, sym)` (mutate + validate + raise), `cell(row, col)`, `symbol_at(row, col)`
  - **Cell** — the smallest class: `is_empty()` — one fact today; tomorrow's facts (blocked? bonus?) land HERE with a `can_place()` rule
  - ❌ Not Game — reaching into squares it doesn't own is feature envy

- **FR-3** — *"players take turns alternately"*
  - **Game** — turns are flow, flow is the orchestrator's: `_turn` stays private; `current_player()` is the only window
  - ❌ Not Board — it doesn't know players exist

- **FR-4** — *"only in an empty cell inside the board"*
  - **Board** — geometry violations (occupied / out-of-bounds): `place()` raises `InvalidMoveError`
  - **Game** — flow violations (moving after the game is over): `make_move()` refuses FIRST, before touching the board
  - The contract detail the demo proves: a rejected move never flips the turn

- **FR-5** — *"K consecutive symbols wins"*
  - **WinRule** — the open variable gets its own object: `winner(board) → Symbol | None`
  - Takes a Board, not a Game — it needs the grid, nothing else
  - Returns a Symbol, not a Player — the rule lives one abstraction below people; **Game** maps symbol → player

- **FR-6** — *"board full and nobody won → draw"*
  - **Board** — states the grid fact: `is_full()` ("every square taken")
  - **Game** — turns facts into the verdict: `status() → GameStatus`
  - Order matters: win is checked *before* full — a winning ninth move is a win, not a draw

- **FR-7** — *"human or bot, bots have difficulty"*
  - **Player** (abstract) — the contract IS the method: `choose_move(board) → (row, col)`
  - **HumanPlayer** — prompts row, then column
  - **BotPlayer** — delegates to `MoveStrategy.choose(board)`, picked from `Difficulty` at construction
  - The payoff: Game can't tell human from bot — that's FR-7 working

- **FR-8** — *"players can see the board after every move"*
  - **Board** — owns the characters: `render() → str`
  - **Game** — surfaces it: `render()` is a pass-through
  - Returns a string, prints nothing — the engine never learns it's a CLI (the NFR)

- **The bonus FR nobody wrote down — undo**
  - We deliberately did NOT build it — and left it as an open exercise ([issue #15](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/issues/15)). The derivation still resolves: whose job would undo be? **Game** — it owns the turn flow
  - The shape of the work: reversing a move needs *memory* of what each move did; what that record must hold is trivial here and explodes for chess (see trade-offs)
  - There's no move-record waiting in the code — that's the point. Bring your design to the PR

## The folder skeleton is a design signal

```
tictactoe/
├── enums.py          Symbol · Difficulty · GameStatus
├── exceptions.py     InvalidMoveError
├── models/
│   ├── __init__.py   re-exports Board, Cell, Player, BotPlayer
│   ├── cell.py       Cell (one fact: symbol)
│   ├── board.py      Board (geometry + occupancy)
│   └── player.py     Player ABC · BotPlayer
├── strategies/
│   ├── win_rule.py   WinRule ABC · KInARowRule
│   └── move_strategy.py  MoveStrategy ABC · RandomMove
├── game.py           Game (the orchestrator)
├── console.py        game-agnostic CLI toolkit
├── cli.py            HumanPlayer · run loop · play() entry
└── main.py           entry point: asserts or `play`
```

- `models/` = pure state, zero I/O — you can test Board with no terminal and no game
- `strategies/` = pluggable rules — swap without touching the rest
- `game.py` = the orchestrator — coordinates turns + win check
- `cli.py` = the I/O adapter — `HumanPlayer` lives here because it needs `input()`; everything else is headless

**`__init__.py` quiz:** if `models/__init__.py` contains `from .board import Board` and a teammate deletes that line, which import in `main.py` breaks? → `from models import Board` (the shortcut). `from models.board import Board` (the direct path) still works. The re-export is a convenience; the underlying module is always reachable.

**The circular-import alarm:** if `Board` imports `Game` and `Game` imports `Board`, that's a cycle — and in Python it's an `ImportError` at runtime, not just a smell. The fix: `Board` should never need `Game`. If it does, the design is backwards (the part reaching up to its whole). Escape hatch for type-hints-only: `from __future__ import annotations` + `if TYPE_CHECKING:` guard.

## Method signatures — no bodies yet

| Class | Method | In | Out | From |
|---|---|---|---|---|
| `Board` | `place(row, col, sym)` | `int, int, Symbol` | `None` (raises `InvalidMoveError`) | FR-1/4 |
| `Board` | `cell(row, col)` | `int, int` | `Cell` | FR-1 |
| `Board` | `symbol_at(row, col)` | `int, int` | `Symbol \| None` | FR-1 |
| `Board` | `is_full()` | — | `bool` | FR-6 |
| `Board` | `render()` | — | `str` | FR-8 |
| `Cell` | `is_empty()` | — | `bool` | FR-1 |
| `WinRule` | `winner(board)` | `Board` | `Symbol \| None` | FR-5 |
| `Player` | `choose_move(board)` | `Board` | `(int, int)` | FR-7 |
| `Game` | `make_move(row, col)` | `int, int` | `None` (raises) | FR-4 |
| `Game` | `status()` | — | `GameStatus` | FR-6 |
| `Game` | `winner()` | — | `Player \| None` | FR-5 |
| `Game` | `current_player()` | — | `Player` | FR-3 |
| `Game` | `render()` | — | `str` | FR-8 |

## The patterns in today's build

1. **Strategy — `WinRule`:** the win condition is the open variable. Default impl: `KInARowRule(k)`. Future swaps: `FourInARowRule`, `GomokuRule(k=5)`. Game doesn't `isinstance`-check; it just calls `rule.winner(board)`. New rules are pure additions.

2. **State (lite) — `GameStatus`:** an enum for now (`IN_PROGRESS` → `WON` / `DRAW`). If asked to expand: introduce `GameStateMachine` with explicit transitions when "paused", "abandoned", "rematch" enter scope.

3. **Factory — assembling players:** `Player` is already an abstract contract. A `PlayerFactory.create("bot", difficulty=Difficulty.HARD)` hides which class + which strategy gets built — `Game` just receives Players.

4. **Command / Memento — the undo you'd reach for:** we didn't build `undo()` — it's an open exercise ([issue #15](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/issues/15)). The pattern it calls for: record each action as a command that carries its own inverse, so reversing is popping the last one. Why not snapshot the whole board each turn? Deep copies cost N×N per move and carry no extra information — a per-move record is the minimal diff.

**The hygiene rule from LLD-21:** introduce these patterns silently in the code, not as announcements. When the interviewer asks "why is `WinRule` a separate class?" the answer is "because the win condition is the open variable across Tic-Tac-Toe, Gomoku, and Connect-Four-style games — making it a Strategy means each new game is one new class, not a forked codebase."

### Edge cases the implementation handles

| Edge case | Where it's caught | What we do |
|---|---|---|
| Move on an occupied cell | `Game.make_move` → `Board.place` | Raise `InvalidMoveError("cell occupied")`; turn doesn't switch |
| Move out of bounds | `Board.place` | Raise `InvalidMoveError("out of bounds")` |
| Move after game over | `Game.make_move` | Raise `InvalidMoveError("game already over")` |
| Board fills with no winner | `Game.status` | Return `GameStatus.DRAW` |
| Winning move & board full simultaneously | `Game.status` | Win takes precedence (check winner BEFORE checking full) |

## Live build — file by file, leaves first

1. **`models/cell.py`** — the simplest class first. `@dataclass Cell` with `symbol: Symbol | None = None` and `is_empty()`. One fact today — the docstring says tomorrow's facts (blocked? bonus? trap?) land HERE.

2. **`models/board.py`** — geometry + occupancy, nothing else. No turns, no rules, no I/O. `place()` raises on occupied or out-of-bounds. The hint comment marks where `blocked` cells would enter: Cell grows `can_place()`, and THIS check asks the cell. One class changes; nothing else.

3. **`strategies/win_rule.py`** — the FR-5 Strategy. `KInARowRule(k)` scans 4 directions (horizontal, vertical, two diagonals) at every cell. Win-check complexity tiers:
   - **Tier 1 — the naive scan** (what we wrote, on purpose): O(n²·k) — for every cell, check k in 4 directions. Correct, readable, and in a 3×3 game the "quadratic" scan touches 36 cells — less work than one Python `print()`.
   - **Tier 2 — only the last move can win:** O(k) — the key insight is that only the player who just moved can have formed a new line, and that line must pass through the square they just placed. Scan only the 4 lines through (last_row, last_col).
   - **Tier 3 — don't scan at all:** O(1) — maintain per-player counters for every row, column, and both diagonals. Each `place()` increments; if any counter == k, that player wins. Caveat: breaks for Gomoku (k < n) because a counter reaching k might count non-consecutive symbols.

4. **`models/player.py` + `strategies/move_strategy.py`** — FR-2 + FR-7. `Player` ABC with `choose_move(board)` abstract method. `BotPlayer` maps `Difficulty` → `MoveStrategy` via a `STRATEGIES` dict. `HumanPlayer` lives in `cli.py` (input adapter, not a model).

5. **`game.py`** — the orchestrator. `make_move(row, col)` does: guard game-over → delegate to board → check win → advance the turn. `status()` checks winner first, then full. There's deliberately no move history and no `undo()` — that's the open exercise ([issue #15](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/issues/15)).

## `console.py` — the game-agnostic CLI toolkit

The validated-input loop pattern: prompt → parse → validate → retry.

~50 lines, zero deps, reusable in every CLI round:
- `ask(prompt, parser, validator)` — the core loop: prompt the user, parse their input, validate it, retry on failure
- `ask_int(prompt)` / `ask_nonempty(prompt)` — common specialisations
- `ask_choice(prompt, options)` / `ask_enum(prompt, enum_cls)` — menu pickers
- `ask_yes_no(prompt)` — boolean shortcut

## The demo output — every FR visible

One run shows every FR: win, all rejections (occupied/OOB/post-game), draw, bot-vs-bot, Gomoku. Run `python3 code/01_tictactoe.py` to see all assertions pass.

## Trade-offs — the last ten minutes

- **Undo — the open exercise:** we didn't ship `undo()` — nobody asked (YAGNI), and it's yours to build ([issue #15](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/issues/15)). The move you reach for is a *record* of each move so the last can be reversed — clear its square, hand the turn back. Why chess breaks this: captures need `captured_piece`, en passant captures from a *different* square, castling moves two pieces, and moving the king destroys castling *rights* — invisible state undo must restore. The record grows into "everything needed to un-happen it" (Command/Memento).

- **Persistence — save the moves, not the board:** build the move-record from the undo exercise and it doubles as the save format: replaying the moves through `make_move()` rebuilds the exact state — board, turn, status. "Save/resume" = store `(players, board config, moves)`; "spectate from move 1" = the same replay.

- **Connect Four — one method away:** `Board.drop(col)`: find the lowest cell in the column with `can_place()`, call the same `place()`. Win rule: `KInARowRule(4)` — already written. Gravity is the only new physics; everything else is reuse.

## The implementation — `code/01_tictactoe.py`

Every line traces to an LLD-22 decision:

| Code | LLD-22 decision |
|---|---|
| `Cell(symbol)` — one fact, still a class | FR-1 — the final design keeps the tiny class so tomorrow's facts (blocked? bonus?) land inside it; the hint comment in `place()` marks the spot |
| `Player` ABC, `HumanPlayer`, `BotPlayer(difficulty)` → `MoveStrategy` | FR-2 + FR-7 — Game can't tell human from bot |
| `(i + 1) % len(players)` | FR-3 — N-player-ready turn pointer |
| `InvalidMoveError` (occupied / out-of-bounds / post-game); rejected move never flips the turn | FR-4 |
| `WinRule` / `KInARowRule(k)` — 4-direction scan, k decoupled from n | FR-5 — Gomoku is `Board(n=5), KInARowRule(k=4)` |
| win checked BEFORE full; `GameStatus` enum | FR-6 |
| `render()` outside `make_move()`; CLI loop separate | FR-8 + the CLI NFR |
| _No_ `moves` list / `undo()` — left as an open exercise | [issue #15](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/issues/15) — students design the move-record and reversal |

## Files

| File | What |
|---|---|
| `index.html` | The interactive class page: relationships → diagram → behaviours-from-FRs → folder structure → APIs → build → CLI → trade-offs (open in a browser for SVG diagrams, quizzes, and click-to-reveal walkthroughs) |
| `code/01_tictactoe.py` | Complete working game in ONE file (read top to bottom) — all demos assert green; `play` arg for the interactive CLI |
| `code/tictactoe/` | **The same engine, organised into a proper package tree** — `enums.py` / `exceptions.py` / `models/` / `strategies/` / `game.py` / `console.py` / `cli.py` / `main.py`. Run `python3 main.py` (acceptance asserts) or `python3 main.py play` |
| `code/tictactoe/console.py` | The game-agnostic console toolkit: `ask` (prompt→parse→validate→retry) + `ask_int` / `ask_nonempty` / `ask_choice` / `ask_enum` / `ask_yes_no` — ~50 lines, zero deps, reusable in every CLI round |

## Next

**LLD-24 — Parking Lot:** bigger entity count, two Strategies from minute one, real concurrency. Same clarify-and-derive method.
