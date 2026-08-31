"""MCP server wrapping the core-banking API (assistants/banking_assistant/api/main.py).

Exposes the same operations as MCP tools by calling the HTTP API, the way a
real ops assistant would talk to a bank's existing systems rather than
touching the database directly. Requires the API to be running (`make api`).

Launched automatically over stdio by the assistant's MCP client config
(see library/agents/specialised.py) — no need to run this by hand.
"""

import os

import httpx
from mcp.server.fastmcp import FastMCP

BANKING_API_URL = os.environ.get("BANKING_API_URL", "http://localhost:8000")

mcp = FastMCP("banking-core-api")


@mcp.tool()
def list_users() -> list[dict]:
    """List all bank customers."""
    resp = httpx.get(f"{BANKING_API_URL}/users")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_user(user_id: int) -> dict:
    """Get a bank customer by id."""
    resp = httpx.get(f"{BANKING_API_URL}/users/{user_id}")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_accounts(user_id: int | None = None) -> list[dict]:
    """List accounts, optionally filtered by user_id."""
    params = {"user_id": user_id} if user_id is not None else {}
    resp = httpx.get(f"{BANKING_API_URL}/accounts", params=params)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_account(account_id: int) -> dict:
    """Get an account by id."""
    resp = httpx.get(f"{BANKING_API_URL}/accounts/{account_id}")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_balance(account_id: int) -> dict:
    """Get the current balance for an account."""
    resp = httpx.get(f"{BANKING_API_URL}/accounts/{account_id}/balance")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def adjust_balance(account_id: int, amount: float, reason: str | None = None) -> dict:
    """Adjust an account's balance by `amount` (positive to credit, negative to debit)."""
    resp = httpx.post(
        f"{BANKING_API_URL}/accounts/{account_id}/balance/adjust",
        json={"amount": amount, "reason": reason},
    )
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_loans(user_id: int | None = None, status: str | None = None) -> list[dict]:
    """List loans, optionally filtered by user_id and/or status."""
    params = {}
    if user_id is not None:
        params["user_id"] = user_id
    if status is not None:
        params["status"] = status
    resp = httpx.get(f"{BANKING_API_URL}/loans", params=params)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_loan(loan_id: int) -> dict:
    """Get a loan by id."""
    resp = httpx.get(f"{BANKING_API_URL}/loans/{loan_id}")
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    mcp.run()
