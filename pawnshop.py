import json
import os
import datetime

data_file = "pawnshop_data.json"
service_fee = 10.0


def load_data():
    if not os.path.exists(data_file):
        return [], 1

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return [], 1
    
    accounts = data.get("accounts", [])
    next_account_id = data.get("next_account_id", 1)

    for acc in accounts:
        if "renewed_date" not in acc and "pawn_date" in acc:
            acc["renewed_date"] = acc["pawn_date"]
        if "maturity_date" not in acc:
            renewed = datetime.date.fromisoformat(acc["renewed_date"])
            maturity = renewed + datetime.timedelta(days=30)
            acc["maturity_date"] = maturity.isoformat()

    return accounts, next_account_id


def save_data(accounts, next_account_id):
    data = {
        "accounts": accounts,
        "next_account_id": next_account_id
    }
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)



def input_date(prompt: str) -> datetime.date:
    while True:
        date_str = input(f"{prompt} (YYYY-MM-DD): ")
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please enter date in YYYY-MM-DD format.\n")



def compute_interest(principal: float, days: int):

    if days > 120:
        return "forfeit"

    if days <= 30:
        total_rate = 0.04
    elif days <= 60:
        total_rate = 0.08
    elif days <= 90:
        total_rate = 0.15
    else:
        total_rate = 0.20

    return principal * total_rate


def pawn_item(accounts, next_account_id):
    print("\n" + "=" * 50)
    print("                 PAWN NEW ITEM")
    print("=" * 50)

    customer_name = input(" Customer name        : ")
    item_description = input(" Item description     : ")

    while True:
        try:
            principal_amount = float(input(" Principal amount (P) : "))
            if principal_amount <= 0:
                raise ValueError
            break
        except ValueError:
            print(" Invalid input. Please enter a valid positive number.\n")

    pawn_date = input_date(" Pawn date")
    maturity_date = pawn_date + datetime.timedelta(days=30)
    forfeit_date = pawn_date + datetime.timedelta(days=120)

    account = {
        "account_id": next_account_id,
        "customer_name": customer_name,
        "item_description": item_description,
        "principal_amount": principal_amount,
        "pawn_date": pawn_date.isoformat(),
        "renewed_date": pawn_date.isoformat(),
        "maturity_date": maturity_date.isoformat(),
        "forfeit_date": forfeit_date.isoformat(),  
        "status": "ACTIVE",
    }

    accounts.append(account)
    next_account_id += 1
    save_data(accounts, next_account_id)

    print("\n" + "-" * 50)
    print("             PAWN TRANSACTION SUMMARY")
    print("-" * 50)
    print(f" Account ID       : {account['account_id']}")
    print(f" Customer Name    : {account['customer_name']}")
    print(f" Item Description : {account['item_description']}")
    print(f" Principal Amount : P{account['principal_amount']:,.2f}")
    print(f" Pawn Date        : {account['pawn_date']}")
    print(f" Maturity Date    : {account['maturity_date']}")
    print(f" Forfeit Date     : {account['forfeit_date']}")
    print(f" Status           : {account['status']}")
    print("-" * 50 + "\n")

    input(" Press Enter to return to main menu...")
    return accounts, next_account_id


def list_accounts(accounts):
    print("\n" + "=" * 50)
    print("              LIST OF ALL ACCOUNTS")
    print("=" * 50)

    if not accounts:
        print(" No accounts found.\n")
        input(" Press Enter to return to main menu...")
        return
    
    for account in accounts:
        print(f" Account ID       : {account['account_id']}")
        print(f" Customer Name    : {account['customer_name']}")
        print(f" Item Description : {account['item_description']}")
        print(f" Principal Amount : P{account['principal_amount']:,.2f}")
        print(f" Pawn Date        : {account['pawn_date']}")
        print(f" Renewed Date     : {account['renewed_date']}")
        print(f" Maturity Date    : {account['maturity_date']}")
        print(f" Forfeit Date     : {account['forfeit_date']}")
        print(f" Status           : {account['status']}")
        print("-" * 50)
    
    print()
    input(" Press Enter to return to main menu...")


def find_account(accounts, account_id: int):
    for account in accounts:
        if account["account_id"] == account_id:
            return account
    return None


def do_transaction(accounts, next_account_id):
    if not accounts:
        print("\n No account found. Pawn first.\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id
    
    print("\n" + "=" * 50)
    print("              TRANSACTION MENU")
    print("=" * 50)

    try:
        get_account_id = int(input(" Enter Account ID: "))
    except ValueError:
        print("\n Invalid Account ID.\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id
    
    account = find_account(accounts, get_account_id)
    if account is None:
        print("\n Account not found.\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id
    
    if account["status"] != "ACTIVE":
        print(f"\n Account status is {account['status']}. No further transactions allowed.\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id

    print("\n" + "-" * 50)
    print("            ACCOUNT INFORMATION")
    print("-" * 50)
    print(f" Account ID       : {account['account_id']}")
    print(f" Customer Name    : {account['customer_name']}")
    print(f" Item Description : {account['item_description']}")
    print(f" Principal Amount : P{account['principal_amount']:,.2f}")
    print(f" Pawn Date        : {account['pawn_date']}")
    print(f" Renewed Date     : {account['renewed_date']}")
    print(f" Maturity Date    : {account.get('maturity_date', 'N/A')}")
    print(f" Forfeit Date     : {account['forfeit_date']}")
    print(f" Status           : {account['status']}")
    print("-" * 50)

    transaction_date = input_date(" Enter date today")
    renewed_date = datetime.date.fromisoformat(account["renewed_date"])
    forfeit_date = datetime.date.fromisoformat(account["forfeit_date"])
    days = (transaction_date - renewed_date).days

    if days < 0:
        print("\n Payment date cannot be before renewed date.\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id

    print(f"\n Days since last pawn/renew : {days} day(s)")

    if transaction_date > forfeit_date:
        account["status"] = "FORFEITED"
        save_data(accounts, next_account_id)
        print("\n Pawn ticket has exceeded the forfeit date.")
        print(f" Item status: {account['status']}\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id

    print("\n [1] Renew Item  (pay interest + service fee)")
    print(" [2] Redeem Item (pay principal + interest + service fee)")
    print(" [3] Forfeit Item (surrender item)")
    print(" [0] Cancel")
    choice = input(" Choose transaction: ")

    if choice not in ["0", "1", "2", "3"]:
        print("\n Invalid choice.\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id

    if choice == "0":
        print("\n Transaction cancelled.\n")
        return accounts, next_account_id

    if choice == "3":
        account["status"] = "FORFEITED"
        save_data(accounts, next_account_id)
        print("\n" + "-" * 50)
        print("              FORFEIT SUMMARY")
        print("-" * 50)
        print(f" Account ID       : {account['account_id']}")
        print(f" Customer Name    : {account['customer_name']}")
        print(f" Item Description : {account['item_description']}")
        print(f" Status           : {account['status']}")
        print("-" * 50 + "\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id

    # For choice 1 or 2, we need interest
    principal = account["principal_amount"]
    interest = compute_interest(principal=principal, days=days)
    if interest == "forfeit":
        account["status"] = "FORFEITED"
        save_data(accounts, next_account_id)
        print("\n Pawn ticket has exceeded 120 days.")
        print(f" Item status: {account['status']}\n")
        input(" Press Enter to return to main menu...")
        return accounts, next_account_id

    rate_percent = (interest / principal) * 100 if principal > 0 else 0

    if choice == "1":
        total_due = interest + service_fee

        print("\n" + "-" * 50)
        print("              RENEWAL SUMMARY")
        print("-" * 50)
        print(f" Days since renew : {days} day(s)")
        print(f" Interest rate    : {rate_percent:.2f}%")
        print(f" Interest amount  : P{interest:,.2f}")
        print(f" Service Fee      : P{service_fee:,.2f}")
        print(f" TOTAL TO PAY     : P{total_due:,.2f}")
        print("-" * 50)

        while True:
            try:
                payment = float(input(" Enter payment amount: P"))
                if payment < total_due:
                    print(f" Insufficient payment. Minimum required is P{total_due:,.2f}\n")
                    continue
                break
            except ValueError:
                print(" Invalid input. Please enter a valid amount.\n")

        change = payment - total_due

        account["renewed_date"] = transaction_date.isoformat()
        new_maturity = transaction_date + datetime.timedelta(days=30)
        new_forfeit = transaction_date + datetime.timedelta(days=120)
        account["maturity_date"] = new_maturity.isoformat()
        account["forfeit_date"] = new_forfeit.isoformat()

        save_data(accounts, next_account_id)

        print("\n" + "-" * 50)
        print("         RENEWAL TRANSACTION DETAILS")
        print("-" * 50)
        print(f" Account ID       : {account['account_id']}")
        print(f" Customer Name    : {account['customer_name']}")
        print(f" Item Description : {account['item_description']}")
        print(f" Principal Amount : P{principal:,.2f}")
        print(f" New Renewed Date : {account['renewed_date']}")
        print(f" New Maturity Date: {account['maturity_date']}")
        print(f" New Forfeit Date : {account['forfeit_date']}")
        print(f" Status           : {account['status']}")
        print(f" Amount Paid      : P{payment:,.2f}")
        print(f" Change           : P{change:,.2f}")
        print("-" * 50 + "\n")

        input(" Press Enter to return to main menu...")
        return accounts, next_account_id

    if choice == "2":
        total_due = principal + interest + service_fee

        print("\n" + "-" * 50)
        print("              REDEEM SUMMARY")
        print("-" * 50)
        print(f" Days since renew : {days} day(s)")
        print(f" Interest rate    : {rate_percent:.2f}%")
        print(f" Principal        : P{principal:,.2f}")
        print(f" Interest         : P{interest:,.2f}")
        print(f" Service Fee      : P{service_fee:,.2f}")
        print(f" TOTAL TO PAY     : P{total_due:,.2f}")
        print("-" * 50)

        while True:
            try:
                payment = float(input(" Enter payment amount: P"))
                if payment < total_due:
                    print(f" Insufficient payment. Minimum required is P{total_due:,.2f}\n")
                    continue
                break
            except ValueError:
                print(" Invalid input. Please enter a valid amount.\n")

        change = payment - total_due

        account["status"] = "REDEEMED"
        save_data(accounts, next_account_id)

        print("\n" + "-" * 50)
        print("        REDEEM TRANSACTION DETAILS")
        print("-" * 50)
        print(f" Account ID       : {account['account_id']}")
        print(f" Customer Name    : {account['customer_name']}")
        print(f" Item Description : {account['item_description']}")
        print(f" Principal Amount : P{principal:,.2f}")
        print(f" Interest         : P{interest:,.2f}")
        print(f" Service Fee      : P{service_fee:,.2f}")
        print(f" Status           : {account['status']}")
        print(f" Amount Paid      : P{payment:,.2f}")
        print(f" Change           : P{change:,.2f}")
        print("-" * 50 + "\n")

        input(" Press Enter to return to main menu...")
        return accounts, next_account_id

    # Just in case
    return accounts, next_account_id



def main():
    accounts, next_account_id = load_data()

    while True:
        print("\n" + "=" * 50)
        print("    WELCOME TO MY PAWNSHOP MANAGEMENT SYSTEM")
        print("=" * 50)
        print(" [1] Pawn New Item")
        print(" [2] List of All Accounts")
        print(" [3] Make a Transaction (Renew / Redeem / Forfeit)")
        print(" [0] Exit")
        choice = input(" Enter choice: ")

        if choice == "1":
            accounts, next_account_id = pawn_item(accounts, next_account_id)
        elif choice == "2":
            list_accounts(accounts)
        elif choice == "3":
            accounts, next_account_id = do_transaction(accounts, next_account_id)
        elif choice == "0":
            print("\n Thank you for using the system. Goodbye!\n")
            break
        else:
            print("\n Invalid choice. Please try again.\n")


if __name__ == "__main__":
    main()
