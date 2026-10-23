"""Config-driven runtime: turns an assistant's assistant.yaml into a running assistant.

config.py   reads and validates assistant.yaml
builder.py  builds the agent (model, MCP tools, RAG tool) from that config
run.py      CLI that runs the declared steps (db, rag, api, start)
app.py      Streamlit entrypoint shared by every assistant
"""
