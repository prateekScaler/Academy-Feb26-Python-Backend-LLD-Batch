"""BookMyShow — the layered package (LLD-27).

The single-file `01_bookmyshow.py` is the teaching scroll; this is the same design
split along its seams so each part can be swapped or tested alone:

    enums / exceptions / config   — the vocabulary and the policy-as-data
    models/                       — domain objects (Seat, Show, ShowSeat, Ticket, ...)
    strategies/                   — the open variables: pricing AND the SeatLocker
                                    (the concurrency approach, pluggable to compare)
    repositories/                 — the storage seam (tickets, payments)
    service.py                    — BookingService, the orchestrator (owns the concurrency)
    console.py / cli.py           — the interactive shell
    main.py                       — `python3 main.py` (acceptance) · `python3 main.py play`
"""
