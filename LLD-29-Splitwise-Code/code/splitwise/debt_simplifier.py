from .models import Payment


class DebtSimplifier:
    """Settle a group in the fewest payments.

    Greedy net-and-match: repeatedly settle the biggest creditor against the
    biggest debtor. This is the standard, practical answer — the *exact* minimum
    number of transactions is NP-hard.
    """

    @staticmethod
    def minimal_payments(nets: dict) -> list:
        creditors = [[u, n] for u, n in nets.items() if n > 0]
        debtors = [[u, -n] for u, n in nets.items() if n < 0]
        payments = []
        while creditors and debtors:
            creditors.sort(key=lambda x: -x[1])
            debtors.sort(key=lambda x: -x[1])
            c, d = creditors[0], debtors[0]
            pay = min(c[1], d[1])
            payments.append(Payment(d[0], c[0], pay))
            c[1] -= pay
            d[1] -= pay
            if c[1] == 0:
                creditors.pop(0)
            if d[1] == 0:
                debtors.pop(0)
        return payments
