"""MCP server wrapping the business-ops API (assistants/business_assistant/api/main.py).

Exposes the same operations as MCP tools by calling the HTTP API, the way a
real ops assistant would talk to a company's existing ERP/CRM system rather
than touching the database directly. Requires the API to be running
(`make api APP=business_assistant`).

Launched automatically over stdio by the assistant's MCP client config
(see library/agents/specialised.py) — no need to run this by hand.
"""

import os

import httpx
from mcp.server.fastmcp import FastMCP

BUSINESS_API_URL = os.environ.get("BUSINESS_API_URL", "http://localhost:8000")

mcp = FastMCP("business-core-api")


@mcp.tool()
def list_customers() -> list[dict]:
    """List all customers."""
    resp = httpx.get(f"{BUSINESS_API_URL}/customers")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_customer(customer_id: int) -> dict:
    """Get a customer by id."""
    resp = httpx.get(f"{BUSINESS_API_URL}/customers/{customer_id}")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_invoices(customer_id: int | None = None, status: str | None = None) -> list[dict]:
    """List invoices, optionally filtered by customer_id and/or status."""
    params = {}
    if customer_id is not None:
        params["customer_id"] = customer_id
    if status is not None:
        params["status"] = status
    resp = httpx.get(f"{BUSINESS_API_URL}/invoices", params=params)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_invoice(invoice_id: int) -> dict:
    """Get an invoice by id."""
    resp = httpx.get(f"{BUSINESS_API_URL}/invoices/{invoice_id}")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def update_invoice_status(invoice_id: int, status: str) -> dict:
    """Update an invoice's status (one of: paid, overdue, pending)."""
    resp = httpx.patch(
        f"{BUSINESS_API_URL}/invoices/{invoice_id}/status",
        json={"status": status},
    )
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_suppliers() -> list[dict]:
    """List all suppliers."""
    resp = httpx.get(f"{BUSINESS_API_URL}/suppliers")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_supplier(supplier_id: int) -> dict:
    """Get a supplier by id."""
    resp = httpx.get(f"{BUSINESS_API_URL}/suppliers/{supplier_id}")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_purchase_orders(
    supplier_id: int | None = None, status: str | None = None
) -> list[dict]:
    """List purchase orders, optionally filtered by supplier_id and/or status."""
    params = {}
    if supplier_id is not None:
        params["supplier_id"] = supplier_id
    if status is not None:
        params["status"] = status
    resp = httpx.get(f"{BUSINESS_API_URL}/purchase_orders", params=params)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_purchase_order(po_id: int) -> dict:
    """Get a purchase order by id."""
    resp = httpx.get(f"{BUSINESS_API_URL}/purchase_orders/{po_id}")
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def update_purchase_order_status(po_id: int, status: str) -> dict:
    """Update a purchase order's status (one of: pending, in_transit, delivered)."""
    resp = httpx.patch(
        f"{BUSINESS_API_URL}/purchase_orders/{po_id}/status",
        json={"status": status},
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    mcp.run()
