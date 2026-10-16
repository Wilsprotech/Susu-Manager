"""Business rules for one rotating susu savings group."""
from dataclasses import dataclass, field
from decimal import Decimal

from money import MoneyError, format_money, parse_money


class SusuError(ValueError):
    """Raised when a requested operation violates a susu rule."""


@dataclass(frozen=True)
class Payout:
    week: int
    recipient: str
    amount: Decimal


@dataclass
class SusuGroup:
    weekly_contribution: Decimal
    members: list[str] = field(default_factory=list)
    current_week: int = 1
    contributions: dict[int, dict[str, Decimal]] = field(default_factory=dict)
    payout_history: list[Payout] = field(default_factory=list)

    @classmethod
    def create(cls, weekly_contribution: str | int | Decimal) -> "SusuGroup":
        try:
            amount = parse_money(weekly_contribution)
        except MoneyError as exc:
            raise SusuError(str(exc)) from exc
        if amount <= 0:
            raise SusuError("The weekly contribution must be greater than zero.")
        return cls(weekly_contribution=amount)

    def add_member(self, name: str) -> None:
        clean_name = name.strip() if isinstance(name, str) else ""
        if not clean_name:
            raise SusuError("Member name or ID cannot be empty.")
        if any(existing.casefold() == clean_name.casefold() for existing in self.members):
            raise SusuError(f"Member '{clean_name}' already exists.")
        # Keep the payout order stable: membership is frozen after activity starts.
        if self.current_week > 1 or any(
            paid > 0
            for week_payments in self.contributions.values()
            for paid in week_payments.values()
        ) or self.payout_history:
            raise SusuError("Members cannot be added after week 1 activity has started.")
        self.members.append(clean_name)
        self.contributions.setdefault(self.current_week, {})[clean_name] = Decimal("0.00")

    def _member_name(self, name: str) -> str:
        if not isinstance(name, str):
            raise SusuError("Unknown member. Add the member before recording a payment.")
        for member in self.members:
            if member.casefold() == name.strip().casefold():
                return member
        raise SusuError(f"Unknown member '{name}'.")

    def record_contribution(self, member_name: str, amount: str | int | Decimal) -> Decimal:
        member = self._member_name(member_name)
        try:
            payment = parse_money(amount)
        except MoneyError as exc:
            raise SusuError(str(exc)) from exc
        if payment <= 0:
            raise SusuError("Contribution must be greater than zero.")
        week_payments = self.contributions.setdefault(self.current_week, {})
        already_paid = week_payments.get(member, Decimal("0.00"))
        owed = self.weekly_contribution - already_paid
        if payment > owed:
            raise SusuError(f"Payment exceeds the amount owed ({format_money(owed)}).")
        week_payments[member] = already_paid + payment
        return self.weekly_contribution - week_payments[member]

    def balances(self) -> dict[str, Decimal]:
        """Return each member's remaining amount due for the current week."""
        week_payments = self.contributions.setdefault(self.current_week, {})
        return {
            member: self.weekly_contribution - week_payments.get(member, Decimal("0.00"))
            for member in self.members
        }

    def close_week(self) -> Payout | None:
        """Close current week if fully funded; otherwise return None without mutation."""
        if not self.members:
            raise SusuError("Add at least one member before closing a week.")
        outstanding = {name: due for name, due in self.balances().items() if due > 0}
        if outstanding:
            details = ", ".join(f"{name} owes {format_money(due)}" for name, due in outstanding.items())
            raise SusuError(f"Week {self.current_week} cannot close. Outstanding: {details}.")

        recipient_index = len(self.payout_history) % len(self.members)
        payout = Payout(
            week=self.current_week,
            recipient=self.members[recipient_index],
            amount=self.weekly_contribution * len(self.members),
        )
        self.payout_history.append(payout)
        self.current_week += 1
        self.contributions.setdefault(self.current_week, {name: Decimal("0.00") for name in self.members})
        return payout

    def report(self) -> str:
        lines = [f"Current week: {self.current_week}", f"Weekly contribution: {format_money(self.weekly_contribution)}", "Members this week:"]
        if not self.members:
            lines.append("  No members have been added yet.")
        for member, due in self.balances().items():
            if due == 0:
                lines.append(f"  {member}: paid in full")
            else:
                paid = self.weekly_contribution - due
                lines.append(f"  {member}: paid {format_money(paid)}; owes {format_money(due)}")
        lines.append("Payout history:")
        if not self.payout_history:
            lines.append("  No payouts yet.")
        else:
            for payout in self.payout_history:
                lines.append(f"  Week {payout.week}: {payout.recipient} received {format_money(payout.amount)}")
        return "\n".join(lines)
