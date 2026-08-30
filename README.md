# ai-assistants (langGraph based)

A small platform for building chat-based ops assistants. Each assistant pairs
a LangGraph agent (via [deepagents](https://github.com/langchain-ai/deepagents))
with a Streamlit chat UI and a FastAPI service that stands in for the
domain's existing backend systems — the way a real ops assistant would call
a bank's core-banking API or a company's ERP, rather than touch a database
directly.

## Quickstart

Requirements: Python 3.10+, `make`.

```bash
# Seed data + start the API and the Streamlit chat UI together (banking_assistant by default)
make start

# Run a different assistant
make start APP=business_assistant

# Just (re)seed the database for an assistant — safe to re-run, drops and recreates tables
make db APP=business_assistant

# Run only the API (no chat UI)
make api APP=banking_assistant

# Tear down the venv and generated dbs
make clean
```

`make start` runs the API in the background and Streamlit in the foreground;
stopping Streamlit (Ctrl+C) shuts the API down too. Once it's up:

- Chat UI: **http://localhost:8501**
- API + Swagger docs: **http://localhost:8000/docs**

## Architecture

Four layers, each one built on the last. Everything below "Business
assistant" is shared code — a new assistant only has to add the
domain-specific row at the bottom.

| Layer | Folder | Owns | Shared across assistants? |
|---|---|---|---|
| 1. Model | `library/models` | Picks the LLM: local Ollama or a remote OpenAI-compatible model | Yes |
| 2. Agent | `library/agents` | Builds the LangGraph deep agent — graph, checkpointer, system prompt, tools | Base class yes, subclass per domain |
| 3. Generic assistant | `library/chatbots` | Streamlit chat shell — message history, thread switching, "New Chat" | Yes |
| 4. Business assistant | `assistants/<name>` | One deployed assistant: entrypoint, FastAPI backend, seed data | No — one per domain |

Reading it top to bottom, each layer wraps the one above it:

- **Model** (`library/models/llm.py`) — `LLMProvider`/`llm` is the one place
  that knows how to construct a chat model, local or remote.
- **Agent** (`library/agents/`) — `generic.py` defines `Assistant`, the base
  class that takes a model, builds the LangGraph graph + SQLite checkpointer,
  and calls `create_deep_agent(...)`. `specialised.py` subclasses it per
  domain (e.g. `BankingOpsAssistant`), overriding `get_system_prompt`,
  `get_tools`, `get_subagents` — this is where a domain's behavior actually
  lives, despite the "Assistant" naming.
- **Generic assistant** (`library/chatbots/generic.py`) — `Chatbot` is a
  Streamlit wrapper that turns *any* agent from the layer above into a chat
  app, with no domain knowledge of its own.
- **Business assistant** (`assistants/<name>/`) — the concrete, deployed
  assistant that ties everything together for one domain:
  - `assistant.py` — entrypoint; instantiates `Chatbot` with a domain agent
  - `api/main.py` — a FastAPI service standing in for that domain's real
    backend (a bank's core-banking API, a company's ERP), which the agent's
    tools call instead of touching the database directly
  - `resources/seed_data.py` — seeds fake data for local development

Each assistant's data — business tables *and* the LangGraph chat-checkpoint
tables — lives in one SQLite file at `db/<name>/<name>.db`.

> **Known limitation:** `library/chatbots/generic.py` currently hardcodes
> `BankingOpsAssistant` in `Chatbot.getAgent()`, so every assistant currently
> runs the banking system prompt regardless of which one you start. Only
> `banking_assistant` behaves as intended today; `business_assistant` needs
> its own specialised agent class and a way for `Chatbot` to pick it.

## Available assistants

| Assistant | Folder | Database | Description |
|---|---|---|---|
| Banking Assistant | `assistants/banking_assistant` | `db/banking_assistant/banking_assistant.db` | Banking operations: users, accounts, balances, loans. |
| Business Assistant | `assistants/business_assistant` | `db/business_assistant/business_assistant.db` | Business operations: customers, invoices, suppliers, purchase orders. |

## API reference

Each assistant's FastAPI service mimics that domain's existing backend
system. It runs on **port 8000** and only touches its own business tables —
never the LangGraph checkpoint tables sharing the same db file.

### Banking Assistant API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/users` | List all users |
| GET | `/users/{user_id}` | Get one user |
| GET | `/accounts?user_id=` | List accounts, optionally filtered by user |
| GET | `/accounts/{account_id}` | Get one account |
| GET | `/accounts/{account_id}/balance` | Get an account's current balance |
| POST | `/accounts/{account_id}/balance/adjust` | Credit/debit an account (`{"amount": float, "reason": str}`); rejects overdrafts |
| GET | `/loans?user_id=&status=` | List loans, optionally filtered by user and/or status |
| GET | `/loans/{loan_id}` | Get one loan |

### Business Assistant API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/customers` | List all customers |
| GET | `/customers/{customer_id}` | Get one customer |
| GET | `/invoices?customer_id=&status=` | List invoices, optionally filtered |
| GET | `/invoices/{invoice_id}` | Get one invoice |
| PATCH | `/invoices/{invoice_id}/status` | Update invoice status (`{"status": "paid"｜"overdue"｜"pending"}`) |
| GET | `/suppliers` | List all suppliers |
| GET | `/suppliers/{supplier_id}` | Get one supplier |
| GET | `/purchase_orders?supplier_id=&status=` | List purchase orders, optionally filtered |
| GET | `/purchase_orders/{po_id}` | Get one purchase order |
| PATCH | `/purchase_orders/{po_id}/status` | Update PO status (`{"status": "pending"｜"in_transit"｜"delivered"}`) |

### Interactive docs (Swagger / ReDoc)

Every assistant's API gets these for free from FastAPI — no extra setup:

- **`http://localhost:8000/docs`** — Swagger UI, try requests directly in the browser
- **`http://localhost:8000/redoc`** — ReDoc, a read-only reference view
- **`http://localhost:8000/openapi.json`** — the raw OpenAPI 3 schema

Since the assistants share port 8000, only one assistant's API can run at a
time today.

## Project structure

```
assistants/
  banking_assistant/
    assistant.py         # Streamlit entrypoint
    api/main.py           # FastAPI service (core-banking API)
    resources/seed_data.py
  business_assistant/
    assistant.py
    api/main.py            # FastAPI service (business-ops API)
    resources/seed_data.py
library/
  models/                 # LLM provider abstraction
  agents/                 # Generic + specialised deep agents
  chatbots/               # Generic Streamlit chat shell
db/
  <app>/<app>.db          # business data + chat checkpoints, one file per assistant
Makefile
requirements.txt
```
