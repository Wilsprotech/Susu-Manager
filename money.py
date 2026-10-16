"""Exact money parsing helpers for Ghana cedi amounts."""
from decimal import Decimal, InvalidOperation


class MoneyError(ValueError):
    """Raised when a money amount is invalid."""


def parse_money(value: str | int | Decimal) -> Decimal:
    """Parse a non-negative amount with at most two decimal places.

    Zero is parsed here but rejected by operations that require a positive payment.
    """
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError) as exc:
        raise MoneyError("Enter a valid amount, for example 50.00.") from exc

    if not amount.is_finite():
        raise MoneyError("Amount must be a finite number.")
    if amount < 0:
        raise MoneyError("Amount cannot be negative.")
    if amount.as_tuple().exponent < -2:
        raise MoneyError("Amounts may have no more than two decimal places.")
    return amount.quantize(Decimal("0.01"))


def format_money(amount: Decimal) -> str:
    """Format a Decimal as a GHS amount with exactly two decimal places."""
    return f"GHS {amount:.2f}"
