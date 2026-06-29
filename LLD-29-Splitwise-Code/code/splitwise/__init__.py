"""Splitwise — layered package. The folder tree IS the architecture:

    money.py / enums.py / exceptions.py   — vocabulary
    models/      ── DOMAIN ──             — User · Group · Split · Expense · Payment
    strategies/  ── OPEN VARIABLE ──      — EqualSplit · ExactSplit · PercentSplit
    balance_sheet.py                      — the running net (who owes whom)
    debt_simplifier.py                    — settle in the fewest payments
    service.py   ── ORCHESTRATOR ──       — ExpenseService
    main.py                               — runnable demos
"""
from .enums import SplitType
from .money import rupees, fmt
from .service import ExpenseService

__all__ = ["SplitType", "rupees", "fmt", "ExpenseService"]
