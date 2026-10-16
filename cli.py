"""Small interactive command-line interface for the susu group."""
from money import format_money
from susu import SusuError, SusuGroup


def main() -> None:
    print("Susu Group Manager")
    while True:
        try:
            weekly_amount = input("Fixed weekly contribution in GHS (e.g. 50.00): ").strip()
            group = SusuGroup.create(weekly_amount)
            break
        except SusuError as exc:
            print(f"Error: {exc}")

    while True:
        print("\n1. Add member\n2. Record contribution\n3. Close current week\n4. Show report\n5. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                name = input("Member name or ID: ")
                group.add_member(name)
                print(f"Added {name.strip()}.")
            elif choice == "2":
                name = input("Member name or ID: ")
                amount = input("Amount paid in GHS: ")
                remaining = group.record_contribution(name, amount)
                print(f"Payment recorded. Remaining balance: {format_money(remaining)}")
            elif choice == "3":
                payout = group.close_week()
                print(f"Week {payout.week} closed. {payout.recipient} receives {format_money(payout.amount)}.")
            elif choice == "4":
                print(group.report())
            elif choice == "5":
                print("Goodbye.")
                return
            else:
                print("Choose a number from 1 to 5.")
        except SusuError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
