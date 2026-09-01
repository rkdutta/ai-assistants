"""Core-banking API for the banking assistant.

Stands in for a bank's existing core-banking system: fronts
db/banking_assistant/banking_assistant.db over HTTP so the assistant (and,
later, an MCP server wrapping this API) talks to it the way a real ops
assistant would talk to a bank's existing systems, rather than touching the
database directly.

Run with: .venv/bin/python assistants/banking_assistant/api/main.py
(from the repo root — that's how `make api` invokes it).
"""

import sqlite3
from datetime import date
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os
from dotenv import load_dotenv

WORKING_DIR = os.environ.get("WORKING_DIR")
load_dotenv(f"{WORKING_DIR}/.env")

APP_KEY = os.environ.get("APP_KEY")
APP_NAME = os.environ.get("APP_NAME")
DB_PATH = Path(f"{WORKING_DIR}/db/{APP_KEY}.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None
    date_of_birth: str


class Account(BaseModel):
    id: int
    user_id: int
    account_number: str
    account_type: str
    status: str
    opened_date: str
    currency: str


class Balance(BaseModel):
    account_id: int
    balance: float
    as_of_date: str


class BalanceAdjustment(BaseModel):
    amount: float
    reason: str | None = None


class Loan(BaseModel):
    id: int
    user_id: int
    loan_type: str
    principal_amount: float
    interest_rate: float
    term_months: int
    outstanding_balance: float
    status: str
    start_date: str
    monthly_payment: float


app = FastAPI(title="Banking Core API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/users", response_model=list[User])
def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)


@app.get("/accounts", response_model=list[Account])
def list_accounts(user_id: int | None = Query(default=None)):
    conn = get_connection()
    if user_id is not None:
        rows = conn.execute(
            "SELECT * FROM accounts WHERE user_id = ? ORDER BY id", (user_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM accounts ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/accounts/{account_id}", response_model=Account)
def get_account(account_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return dict(row)


@app.get("/accounts/{account_id}/balance", response_model=Balance)
def get_balance(account_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM balances WHERE account_id = ?", (account_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return dict(row)


@app.post("/accounts/{account_id}/balance/adjust", response_model=Balance)
def adjust_balance(account_id: int, adjustment: BalanceAdjustment):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM balances WHERE account_id = ?", (account_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Account not found")

    new_balance = row["balance"] + adjustment.amount
    if new_balance < 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient funds")

    conn.execute(
        "UPDATE balances SET balance = ?, as_of_date = ? WHERE account_id = ?",
        (new_balance, date.today().isoformat(), account_id),
    )
    conn.commit()
    updated = conn.execute(
        "SELECT * FROM balances WHERE account_id = ?", (account_id,)
    ).fetchone()
    conn.close()
    return dict(updated)


@app.get("/loans", response_model=list[Loan])
def list_loans(
    user_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
):
    conn = get_connection()
    clauses = []
    params = []
    if user_id is not None:
        clauses.append("user_id = ?")
        params.append(user_id)
    if status is not None:
        clauses.append("status = ?")
        params.append(status)
    query = "SELECT * FROM loans"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/loans/{loan_id}", response_model=Loan)
def get_loan(loan_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return dict(row)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8001)))
