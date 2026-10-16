# Susu Group Manager

A small Python command-line application for managing one rotating savings (susu) group. Members contribute the same fixed amount each week, and the full pot is paid to one member in join order after everyone has paid in full.

## Requirements

- Python 3.11 or newer
- No third-party packages required

## Run the program

From the project directory:

```bash
python cli.py
```

Enter the group's fixed weekly contribution in GHS, then use the menu to add members, record full or partial contributions, close the week, or view the report.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

The test suite covers partial payments, blocked week closure, payout amount and order, duplicate and unknown members, invalid payments, overpayments, exact decimal handling, membership restrictions, reporting, and empty groups.

## Example workflow

For three members and a weekly contribution of GHS 50.00:

1. Add Ama, Kofi, and Esi in that order.
2. Record GHS 50.00 for Ama, GHS 50.00 for Kofi, and GHS 30.00 for Esi.
3. Attempt to close the week. It is blocked and reports that Esi owes GHS 20.00.
4. Record Esi's remaining GHS 20.00 and close the week again.
5. Ama receives GHS 150.00, and week 2 begins with Kofi next in the payout order.

## Design notes

- Money is represented with `decimal.Decimal`; binary floating-point arithmetic is not used.
- The core business rules are in `susu.py`, money parsing/formatting is in `money.py`, and the CLI is in `cli.py`.
- Data is held in memory and resets when the program exits; persistence is listed as a future improvement in `NOTES.md`.
