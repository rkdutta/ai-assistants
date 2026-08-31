"""Core business-ops API for the business assistant.

Stands in for a company's existing ERP/CRM system: fronts
db/business_assistant/business_assistant.db over HTTP so the assistant (and,
later, an MCP server wrapping this API) talks to it the way a real ops
assistant would talk to existing systems, rather than touching the database
directly. Only touches customers/invoices/suppliers/purchase_orders — leaves
the LangGraph checkpoint tables also stored in this db untouched.

Run with: .venv/bin/python assistants/business_assistant/api/main.py
(from the repo root — that's how `make api APP=business_assistant` invokes it).
"""

import sqlite3
from pathlib import Path
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv

WORKING_DIR = os.environ.get("WORKING_DIR")
load_dotenv(f"{WORKING_DIR}.env")

APP_KEY = os.environ.get("APP_KEY")
APP_NAME = os.environ.get("APP_NAME")
DB_PATH = Path(f"{WORKING_DIR}/db/{APP_KEY}.db")

INVOICE_STATUSES = {"paid", "overdue", "pending"}
PURCHASE_ORDER_STATUSES = {"pending", "in_transit", "delivered"}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    notes: str | None


class Invoice(BaseModel):
    id: int
    customer_id: int
    amount: float
    status: str
    issued_date: str
    due_date: str


class InvoiceStatusUpdate(BaseModel):
    status: str


class Supplier(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    notes: str | None


class PurchaseOrder(BaseModel):
    id: int
    supplier_id: int
    item: str
    quantity: int
    status: str
    order_date: str


class PurchaseOrderStatusUpdate(BaseModel):
    status: str


app = FastAPI(title="Business Ops Core API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/customers", response_model=list[Customer])
def list_customers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM customers ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM customers WHERE id = ?", (customer_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return dict(row)


@app.get("/invoices", response_model=list[Invoice])
def list_invoices(
    customer_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
):
    conn = get_connection()
    clauses = []
    params = []
    if customer_id is not None:
        clauses.append("customer_id = ?")
        params.append(customer_id)
    if status is not None:
        clauses.append("status = ?")
        params.append(status)
    query = "SELECT * FROM invoices"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/invoices/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return dict(row)


@app.patch("/invoices/{invoice_id}/status", response_model=Invoice)
def update_invoice_status(invoice_id: int, update: InvoiceStatusUpdate):
    if update.status not in INVOICE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {sorted(INVOICE_STATUSES)}",
        )
    conn = get_connection()
    row = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Invoice not found")

    conn.execute(
        "UPDATE invoices SET status = ? WHERE id = ?", (update.status, invoice_id)
    )
    conn.commit()
    updated = conn.execute(
        "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
    ).fetchone()
    conn.close()
    return dict(updated)


@app.get("/suppliers", response_model=list[Supplier])
def list_suppliers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM suppliers ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/suppliers/{supplier_id}", response_model=Supplier)
def get_supplier(supplier_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM suppliers WHERE id = ?", (supplier_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return dict(row)


@app.get("/purchase_orders", response_model=list[PurchaseOrder])
def list_purchase_orders(
    supplier_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
):
    conn = get_connection()
    clauses = []
    params = []
    if supplier_id is not None:
        clauses.append("supplier_id = ?")
        params.append(supplier_id)
    if status is not None:
        clauses.append("status = ?")
        params.append(status)
    query = "SELECT * FROM purchase_orders"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/purchase_orders/{po_id}", response_model=PurchaseOrder)
def get_purchase_order(po_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM purchase_orders WHERE id = ?", (po_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return dict(row)


@app.patch("/purchase_orders/{po_id}/status", response_model=PurchaseOrder)
def update_purchase_order_status(po_id: int, update: PurchaseOrderStatusUpdate):
    if update.status not in PURCHASE_ORDER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {sorted(PURCHASE_ORDER_STATUSES)}",
        )
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM purchase_orders WHERE id = ?", (po_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Purchase order not found")

    conn.execute(
        "UPDATE purchase_orders SET status = ? WHERE id = ?", (update.status, po_id)
    )
    conn.commit()
    updated = conn.execute(
        "SELECT * FROM purchase_orders WHERE id = ?", (po_id,)
    ).fetchone()
    conn.close()
    return dict(updated)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
