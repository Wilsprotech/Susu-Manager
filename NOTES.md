# Assumptions, decisions, and future improvements

## Assumptions and decisions

1. **Member identity:** a trimmed name or ID is the member identifier. Duplicate identifiers are rejected case-insensitively, so `Ama` and `ama` are considered the same member.
2. **Fixed amount:** the group's weekly contribution is set at creation and must be positive. Each member owes that amount in every active week.
3. **Currency precision:** amounts must be valid finite decimal values with at most two decimal places. GHS amounts are stored and calculated using `Decimal` and displayed with two decimal places.
4. **Partial payments:** a member may pay in multiple positive installments during the current week. The outstanding balance is the weekly contribution minus the sum of their installments.
5. **Overpayments:** a payment larger than the member's remaining balance is rejected; excess money is not carried into another week.
6. **Closing a week:** closure is atomic from the user's perspective. If any member owes money, the operation raises an error listing each outstanding balance and makes no payout, week increment, or payout-history entry.
7. **Payout order:** the first member added receives the first pot, then the second, and so on. After the last member receives a pot, the order cycles back to the first member.
8. **Membership changes:** members can be added only before the first contribution is recorded. This keeps pot size and payout order stable for the entire cycle. Member removal is not supported.
9. **Empty group:** a week cannot close until at least one member has been added.
10. **Persistence:** this is a small demonstration CLI, so data is held in memory and is lost when the program exits.

## What I would improve with more time

- Add SQLite persistence and schema migrations so groups, weekly contributions, and payouts survive restarts.
- Add a transaction/audit log with timestamps and a way to correct mistakes without silently rewriting history.
- Add multiple groups, explicit member IDs, and controlled member lifecycle rules.
- Add stronger CLI input ergonomics and optional JSON export of reports.
- Add property-based tests for long sequences of payments and payout rotations, plus static analysis and continuous integration.
- Consider concurrency and transactional safeguards if the app becomes a shared API or multi-user service.
