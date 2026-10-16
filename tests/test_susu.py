import unittest
from decimal import Decimal

from money import MoneyError, parse_money
from susu import SusuError, SusuGroup


class SusuGroupTests(unittest.TestCase):
    def setUp(self):
        self.group = SusuGroup.create("50.00")
        for name in ("Ama", "Kofi", "Esi"):
            self.group.add_member(name)

    def test_partial_payment_and_remaining_balance(self):
        remaining = self.group.record_contribution("Esi", "30.00")
        self.assertEqual(remaining, Decimal("20.00"))
        self.assertEqual(self.group.balances()["Esi"], Decimal("20.00"))

    def test_week_cannot_close_when_member_owes(self):
        self.group.record_contribution("Ama", "50.00")
        self.group.record_contribution("Kofi", "50.00")
        self.group.record_contribution("Esi", "30.00")
        with self.assertRaisesRegex(SusuError, "Esi owes GHS 20.00"):
            self.group.close_week()
        self.assertEqual(self.group.current_week, 1)
        self.assertEqual(self.group.payout_history, [])

    def test_full_payment_closes_week_and_pays_first_member(self):
        for name in self.group.members:
            self.group.record_contribution(name, "50.00")
        payout = self.group.close_week()
        self.assertEqual(payout.recipient, "Ama")
        self.assertEqual(payout.amount, Decimal("150.00"))
        self.assertEqual(self.group.current_week, 2)

    def test_next_payout_follows_join_order(self):
        for _ in range(2):
            for name in self.group.members:
                self.group.record_contribution(name, "50.00")
            self.group.close_week()
        self.assertEqual([p.recipient for p in self.group.payout_history], ["Ama", "Kofi"])

    def test_duplicate_member_is_rejected_case_insensitively(self):
        with self.assertRaisesRegex(SusuError, "already exists"):
            self.group.add_member("ama")

    def test_unknown_member_is_rejected(self):
        with self.assertRaisesRegex(SusuError, "Unknown member"):
            self.group.record_contribution("Yaw", "10.00")

    def test_zero_and_negative_payments_are_rejected(self):
        for amount in ("0", "-1.00"):
            with self.subTest(amount=amount), self.assertRaises(SusuError):
                self.group.record_contribution("Ama", amount)

    def test_overpayment_is_rejected_without_changing_balance(self):
        self.group.record_contribution("Ama", "40.00")
        with self.assertRaisesRegex(SusuError, "exceeds"):
            self.group.record_contribution("Ama", "10.01")
        self.assertEqual(self.group.balances()["Ama"], Decimal("10.00"))

    def test_more_than_two_decimal_places_is_rejected(self):
        with self.assertRaises(MoneyError):
            parse_money("1.005")

    def test_membership_freezes_after_contributions_start(self):
        self.group.record_contribution("Ama", "1.00")
        with self.assertRaisesRegex(SusuError, "cannot be added"):
            self.group.add_member("Yaw")

    def test_report_shows_paid_status_and_payout_history(self):
        for name in self.group.members:
            self.group.record_contribution(name, "50.00")
        self.group.close_week()
        report = self.group.report()
        self.assertIn("Current week: 2", report)
        self.assertIn("Ama received GHS 150.00", report)
        self.assertIn("Ama: paid GHS 0.00; owes GHS 50.00", report)

    def test_group_rejects_zero_or_negative_weekly_amount(self):
        for amount in ("0", "-5.00"):
            with self.subTest(amount=amount), self.assertRaises(SusuError):
                SusuGroup.create(amount)

    def test_empty_group_cannot_close(self):
        with self.assertRaisesRegex(SusuError, "at least one member"):
            SusuGroup.create("50.00").close_week()


if __name__ == "__main__":
    unittest.main()
