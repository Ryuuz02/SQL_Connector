import psycopg2
from datetime import date

names = {"customer": [], "teller": [], "manager": []}
login_type = ""
name = ""


def login():
    global name, login_type
    name = input("Please enter your name")
    if name in names["customer"]:
        login_type = "customer"
    elif name in names["teller"]:
        login_type = "teller"
    elif name in names["manager"]:
        login_type = "manager"
    else:
        print("That is not an accepted login")


DB_NAME = "homework"
DB_USER = "postgres"
DB_PASS = "password"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
print("Database connected successfully")
cur = conn.cursor()
cur.execute("SELECT name FROM customer;")
names["customer"] = cur.fetchone()
cur.execute("SELECT name FROM employee WHERE emp_type = 'teller';")
names["teller"] = cur.fetchone()
cur.execute("SELECT name FROM employee WHERE emp_type = 'manager';")
names["manager"] = cur.fetchone()
login()


def withdrawal():
    account_id = input("What account id would you like to withdraw from?")
    cur.execute("SELECT name FROM customer_account WHERE account_id = %s", account_id)
    account_name = cur.fetchone()[0]
    if login_type == "customer" and name != account_name:
        print("That is not your account")
    else:
        cur.execute("SELECT balance FROM account WHERE account_id = %s", account_id)
        balance = int(cur.fetchone()[0])
        withdraw = int(input("How much would you like to withdraw?"))
        if withdraw > balance:
            print("You do not have enough in your balance to withdraw that")
        else:
            cur.execute("SELECT MAX(trans_id) FROM transaction")
            trans_id = int(cur.fetchone())
            trans_id = str(trans_id + 1)
            diff = balance - withdraw
            cur.execute("UPDATE account SET balance = %s WHERE account_id = %s", (diff, account_id))
            cur.execute("INSERT INTO transaction (trans_id, account_id, trans_type, amount, date "
                        "VALUES(%s, %s, Interest, %s, %s, Null)", (trans_id, account_id, "withdraw", str(-withdraw),
                                                                   str(date.today())))


def deposit():
    account_id = input("What account id would you like to deposit into?")
    cur.execute("SELECT name FROM customer_account WHERE account_id = %s", account_id)
    account_name = cur.fetchone()[0]
    if login_type == "customer" and name != account_name:
        print("That is not your account")
    else:
        cur.execute("SELECT balance FROM account WHERE account_id = %s", account_id)
        balance = int(cur.fetchone()[0])
        deposit_amount = int(input("How much would you like to deposit?"))
        cur.execute("SELECT MAX(trans_id) FROM transaction")
        trans_id = int(cur.fetchone()[0])
        trans_id = str(trans_id + 1)
        diff = balance + deposit_amount
        cur.execute("UPDATE account SET balance = %s WHERE account_id = %s", (diff, account_id))
        cur.execute("INSERT INTO transaction (trans_id, account_id, trans_type, amount, date "
                    "VALUES(%s, %s, Interest, %s, %s, Null)", (trans_id, account_id, "deposit", str(deposit_amount),
                                                               str(date.today())))


def transfer():
    account_id = input("What account id would you like to transfer from?")
    cur.execute("SELECT name FROM customer_account WHERE account_id = %s", account_id)
    account_name = cur.fetchone()[0]
    if login_type == "customer" and name != account_name:
        print("That is not your account")
    else:
        cur.execute("SELECT balance FROM account WHERE account_id = %s", account_id)
        balance = int(cur.fetchone()[0])
        transfer_amount = int(input("How much would you like to transfer?"))
        if transfer_amount > balance:
            print("You do not have enough in your balance to withdraw that")
        else:
            transfer_id = input("What account id would you like to transfer to?")
            cur.execute("SELECT MAX(trans_id) FROM transaction")
            trans_id = int(cur.fetchone()[0])
            trans_id = str(trans_id + 1)
            diff = balance - transfer_amount
            cur.execute("UPDATE account SET balance = %s WHERE account_id = %s", (diff, account_id))
            cur.execute("SELECT balance FROM account WHERE account_id = %s", account_id)
            balance = int(cur.fetchone()[0])
            add = balance + transfer_amount
            cur.execute("UPDATE account SET balance = %s WHERE account_id = %s", (add, transfer_id))
            cur.execute("INSERT INTO transaction (trans_id, account_id, trans_type, amount, date "
                        "VALUES(%s, %s, Interest, %s, %s, Null)", (trans_id, account_id, "transfer",
                                                                   str(-transfer_amount), str(date.today())))


def external_transfer():
    account_id = input("What account id would you like to withdraw from?")
    cur.execute("SELECT name FROM customer_account WHERE account_id = %s", account_id)
    account_name = cur.fetchone()[0]
    if login_type == "customer" and name != account_name:
        print("That is not your account")
    else:
        cur.execute("SELECT balance FROM account WHERE account_id = %s", account_id)
        balance = int(cur.fetchone()[0])
        transfer_amount = int(input("How much would you like to transfer?"))
        if transfer_amount > balance:
            print("You do not have enough in your balance to withdraw that")
        else:
            cur.execute("SELECT MAX(trans_id) FROM transaction")
            trans_id = int(cur.fetchone()[0])
            trans_id = str(trans_id + 1)
            diff = balance - transfer_amount
            cur.execute("UPDATE account SET balance = %s WHERE account_id = %s", (diff, account_id))
            cur.execute("INSERT INTO transaction (trans_id, account_id, trans_type, amount, date "
                        "VALUES(%s, %s, Interest, %s, %s, Null)", (trans_id, account_id, "external transfer",
                                                                   str(-transfer_amount), str(date.today())))


def create():
    if login_type != "teller":
        account_type = input("What account type would you like?")
        if login_type == "manager":
            customer = input("Whose name is this account under?")
        else:
            customer = name
        cur.execute("SELECT MAX(account_id) FROM account")
        account_id = int(cur.fetchone()[0])
        account_id = str(account_id + 1)
        cur.execute("INSERT INTO account (account_id, acc_type, balance) VALUES(%s, %s, %s)",
                    (account_id, account_type, "0"))
        cur.execute("SELECT (address, branch_id) FROM customer WHERE name = %s", (customer))
        addr_branch = cur.fetchone()[0]
        addr_branch = addr_branch[1:-1]
        addr_branch = list(addr_branch.split(','))
        print(addr_branch)
        cur.execute("INSERT INTO customer_account (name, address, branch_id, account_id) VALUES (%s, %s, %s, %s)",
                    (customer, addr_branch[0], addr_branch[1], account_id))
        print("created account")
    else:
        print("Your account does not have access to this feature")


def delete():
    if login_type != "teller":
        account_id = input("What account id would you like to delete?")
        cur.execute("SELECT name FROM customer_account WHERE account_id = %s", account_id)
        account_name = cur.fetchone()[0]
        if login_type == "customer" and name != account_name:
            print("That is not your account")
        else:
            cur.execute("DELETE FROM account WHERE account_id = %s", account_id)
            cur.execute("DELETE FROM customer_account WHERE account_id = %s", account_id)
    else:
        print("Your account does not have access to this feature")


def show_statement():
    if login_type != "teller":
        account_id = input("What account id would you like to see the statement for?")
        cur.execute("SELECT name FROM customer_account WHERE account_id = %s", account_id)
        account_name = cur.fetchone()[0]
        if login_type == "customer" and name != account_name:
            print("That is not your account")
        else:
            statement_year = input("What year would you like to see the statement for? (use YYYY format)")
            statement_month = input("What month would you like to see the statement for? (use MM format)")
            cur.execute("SELECT date, trans_type, amount, description FROM transaction WHERE account_id = %s and %s = "
                        "date_part('month', date) and %s = date_part('year', date)",
                        (account_id, statement_month, statement_year))
            trans = cur.fetchall()
            for transaction in trans:
                trans_date = str(transaction[0])
                trans_type = str(transaction[1])
                amount = str(transaction[2])
                desc = str(transaction[3])
                print(trans_date + " " + trans_type + " " + amount + " Description: " + desc)
    else:
        print("Your account does not have access to this feature")


def pending_trans():
    if login_type != "teller":
        account_id = input("What account id would you like to see the pending transactions for?")
        cur.execute("SELECT name FROM customer_account WHERE account_id = %s", account_id)
        account_name = cur.fetchone()[0]
        if login_type == "customer" and name != account_name:
            print("That is not your account")
        else:
            current_date = str(date.today())
            current_year = current_date[0:4]
            current_month = current_date[5:7]
            cur.execute("SELECT date, trans_type, amount, description FROM transaction WHERE account_id = %s and %s = "
                        "date_part('month', date) and %s = date_part('year', date)",
                        (account_id, current_month, current_year))
            trans = cur.fetchall()
            for transaction in trans:
                trans_date = str(transaction[0])
                trans_type = str(transaction[1])
                amount = str(transaction[2])
                desc = str(transaction[3])
                print(trans_date + " " + trans_type + " " + amount + " Description: " + desc)
    else:
        print("Your account does not have access to this feature")


def add_fees():
    if login_type == "manager":
        cur.execute("SELECT account_id from account")
        accounts = cur.fetchall()

        print(accounts)
        for account in accounts:
            account = str(account[0])
            print(account)
            cur.execute("SELECT acc_type FROM account WHERE account_id = %s", account)
            account_type = cur.fetchone()[0]
            if account_type == "saving":
                cur.execute("SELECT balance FROM account WHERE account_id = %s", account)
                balance = int(cur.fetchone()[0])
                interest_balance = str(balance * 1.1)
                interest = str(balance * 0.1)
                cur.execute("SELECT MAX(trans_id) FROM transaction")
                trans_id = int(cur.fetchone()[0])
                trans_id = str(trans_id + 1)
                cur.execute("UPDATE account SET balance = %s WHERE account_id = %s", (interest_balance, account))
                cur.execute("INSERT INTO transaction (trans_id, account_id, trans_type, amount, date, description) "
                            "VALUES(%s, %s, %s, %s, %s, %s)", (trans_id, account, "interest", interest,
                                                               str(date.today()), "fee"))
            if account_type == "checking":
                cur.execute("SELECT balance FROM account WHERE account_id = %s", account)
                balance = int(cur.fetchone()[0])
                if balance < 0:
                    fee_balance = str(balance - 50)
                    cur.execute("SELECT MAX(trans_id) FROM transaction")
                    trans_id = int(cur.fetchone())
                    trans_id = str(trans_id + 1)
                    cur.execute("INSERT INTO transaction (trans_id, account_id, trans_type, amount, date, description) "
                                "VALUES(%s, %s, %s, %s, %s, %s)", (trans_id, account, "overdraft fee", "-50",
                                                                   str(date.today()), "overdraft fee"))
                    cur.execute("UPDATE account SET balance = %s WHERE account_id = %s", (fee_balance, account))
                else:
                    pass

    else:
        print("Your account does not have access to this feature")


def total_balance():
    if login_type == "manager":
        branch_id = input("Which branch id would you like to total?")
        total = 0
        cur.execute("SELECT account_id FROM customer_account WHERE branch_id = %s", (branch_id,))
        account_ids = cur.fetchall()
        for account in account_ids:
            account = str(account[0])
            cur.execute("SELECT balance FROM account WHERE account_id = %s", (account,))
            total += int(cur.fetchone()[0])
        print("The total balance of all accounts is: " + str(total))
    else:
        print("Your account does not have access to that feature")


def num_of_accounts():
    if login_type == "manager":
        branch_id = input("Which branch id would you like to total?")
        cur.execute("SELECT count(account_id) FROM customer_account WHERE branch_id = %s", (branch_id,))
        total = str(cur.fetchone()[0])
        print("The total number of accounts is: " + total)
    else:
        print("Your account does not have access to that feature")


running = True
while running:
    choice = input("1: Withdrawal\n"
                   "2: Deposit\n"
                   "3: Transfer\n"
                   "4: External Transfer\n"
                   "5: Create Account\n"
                   "6: Delete Account\n"
                   "7: Show Statement\n"
                   "8: Pending Transactions\n"
                   "9: Add Fees\n"
                   "10: Total Balance\n"
                   "11: Number of Accounts\n"
                   "12: Exit\n")
    if choice == "1":
        withdrawal()
    elif choice == "2":
        deposit()
    elif choice == "3":
        transfer()
    elif choice == "4":
        external_transfer()
    elif choice == "5":
        create()
    elif choice == "6":
        delete()
    elif choice == "7":
        show_statement()
    elif choice == "8":
        pending_trans()
    elif choice == "9":
        add_fees()
    elif choice == "10":
        total_balance()
    elif choice == "11":
        num_of_accounts()
    elif choice == "12":
        running = False
    else:
        pass

cur.close()
# conn.commit()
conn.close()




