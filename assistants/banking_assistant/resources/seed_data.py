"""Seeds db/banking_assistant/banking_assistant.db with fake users/accounts/
balances/loans data.

Run with: .venv/bin/python assistants/banking_assistant/db/seed_data.py
(from the repo root — that's how `make start` / `make seed-db` invoke it).
Re-running drops and recreates these tables, so it's safe to repeat.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("db/banking_assistant/banking_assistant.db")

USERS = [
    (1, "Ava", "Nguyen", "ava.nguyen@example.com", "+1-555-0301", "1987-03-14"),
    (2, "Marcus", "Lee", "marcus.lee@example.com", "+1-555-0302", "1990-07-22"),
    (3, "Priya", "Shah", "priya.shah@example.com", "+1-555-0303", "1979-11-02"),
    (4, "Oliver", "Bennett", "oliver.bennett@example.com", "+1-555-0304", "1995-01-30"),
    (5, "Sofia", "Garcia", "sofia.garcia@example.com", "+1-555-0305", "1983-09-18"),
    (6, "Ethan", "Walker", "ethan.walker@example.com", "+1-555-0306", "1972-05-09"),
    (7, "Grace", "Kim", "grace.kim@example.com", "+1-555-0307", "1998-12-25"),
    (8, "Noah", "Johansson", "noah.johansson@example.com", "+1-555-0308", "1989-04-11"),
    (9, "Ines", "Moreau", "ines.moreau@example.com", "+1-555-0309", "1993-08-07"),
    (10, "Daniel", "Okafor", "daniel.okafor@example.com", "+1-555-0310", "1985-02-19"),
]

# user_id references USERS.id
ACCOUNTS = [
    (1, 1, "AC-100001", "checking", "active", "2019-06-01", "USD"),
    (2, 1, "AC-100002", "savings", "active", "2019-06-01", "USD"),
    (3, 2, "AC-100003", "checking", "active", "2021-02-15", "USD"),
    (4, 3, "AC-100004", "checking", "active", "2015-10-09", "USD"),
    (5, 3, "AC-100005", "savings", "active", "2015-10-09", "USD"),
    (6, 4, "AC-100006", "checking", "active", "2023-04-03", "USD"),
    (7, 5, "AC-100007", "checking", "frozen", "2018-01-20", "USD"),
    (8, 5, "AC-100008", "savings", "active", "2018-01-20", "USD"),
    (9, 6, "AC-100009", "business", "active", "2012-07-11", "USD"),
    (10, 7, "AC-100010", "checking", "active", "2024-03-28", "USD"),
    (11, 8, "AC-100011", "checking", "active", "2020-09-14", "USD"),
    (12, 9, "AC-100012", "savings", "active", "2022-05-30", "USD"),
    (13, 10, "AC-100013", "checking", "closed", "2016-11-02", "USD"),
    (14, 10, "AC-100014", "business", "active", "2016-11-02", "USD"),
]

# account_id references ACCOUNTS.id
BALANCES = [
    (1, 1, 4250.32, "2026-08-29"),
    (2, 2, 18760.00, "2026-08-29"),
    (3, 3, 1120.55, "2026-08-29"),
    (4, 4, 9875.10, "2026-08-29"),
    (5, 5, 42300.00, "2026-08-29"),
    (6, 6, 530.00, "2026-08-29"),
    (7, 7, 0.00, "2026-08-29"),
    (8, 8, 15200.75, "2026-08-29"),
    (9, 9, 87650.20, "2026-08-29"),
    (10, 10, 2100.40, "2026-08-29"),
    (11, 11, 6430.18, "2026-08-29"),
    (12, 12, 25800.00, "2026-08-29"),
    (13, 13, 0.00, "2026-08-29"),
    (14, 14, 132400.65, "2026-08-29"),
]

# user_id references USERS.id
LOANS = [
    (1, 1, "mortgage", 320000.00, 4.25, 360, 298450.10, "active", "2020-05-01", 1574.00),
    (2, 2, "auto", 28000.00, 6.10, 60, 15230.75, "active", "2023-09-12", 542.00),
    (3, 4, "student", 45000.00, 5.50, 120, 39800.00, "active", "2022-08-01", 487.00),
    (4, 5, "personal", 10000.00, 9.75, 36, 0.00, "paid_off", "2019-03-15", 0.00),
    (5, 6, "mortgage", 510000.00, 3.90, 360, 402100.50, "active", "2011-06-01", 2410.00),
    (6, 9, "auto", 22000.00, 7.20, 48, 21100.00, "delinquent", "2025-01-20", 528.00),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS loans")
    cur.execute("DROP TABLE IF EXISTS balances")
    cur.execute("DROP TABLE IF EXISTS accounts")
    cur.execute("DROP TABLE IF EXISTS users")

    cur.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            date_of_birth TEXT NOT NULL
        )
        """
    )
    cur.executemany(
        "INSERT INTO users (id, first_name, last_name, email, phone, date_of_birth) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        USERS,
    )

    cur.execute(
        """
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            account_number TEXT NOT NULL UNIQUE,
            account_type TEXT NOT NULL CHECK (account_type IN ('checking', 'savings', 'business')),
            status TEXT NOT NULL CHECK (status IN ('active', 'frozen', 'closed')),
            opened_date TEXT NOT NULL,
            currency TEXT NOT NULL
        )
        """
    )
    cur.executemany(
        "INSERT INTO accounts (id, user_id, account_number, account_type, status, opened_date, currency) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ACCOUNTS,
    )

    cur.execute(
        """
        CREATE TABLE balances (
            id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL UNIQUE REFERENCES accounts(id),
            balance REAL NOT NULL,
            as_of_date TEXT NOT NULL
        )
        """
    )
    cur.executemany(
        "INSERT INTO balances (id, account_id, balance, as_of_date) VALUES (?, ?, ?, ?)",
        BALANCES,
    )

    cur.execute(
        """
        CREATE TABLE loans (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            loan_type TEXT NOT NULL CHECK (loan_type IN ('mortgage', 'auto', 'personal', 'student')),
            principal_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            term_months INTEGER NOT NULL,
            outstanding_balance REAL NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('active', 'paid_off', 'delinquent')),
            start_date TEXT NOT NULL,
            monthly_payment REAL NOT NULL
        )
        """
    )
    cur.executemany(
        "INSERT INTO loans (id, user_id, loan_type, principal_amount, interest_rate, term_months, "
        "outstanding_balance, status, start_date, monthly_payment) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        LOANS,
    )

    conn.commit()
    conn.close()
    print(
        f"Seeded {len(USERS)} users, {len(ACCOUNTS)} accounts, "
        f"{len(BALANCES)} balances, {len(LOANS)} loans into {DB_PATH}"
    )


if __name__ == "__main__":
    seed()
