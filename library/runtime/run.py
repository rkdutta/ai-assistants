"""Runs the steps an assistant declares in its assistant.yaml.

Usage (from the repo root): WORKING_DIR=assistants/<name> python -m library.runtime.run <db|rag|api|start>
Steps the assistant doesn't declare are skipped.

db     run the seed script        rag    index the docs folder into Chroma
api    run the API (foreground)   start  db + rag + API in background + Streamlit
"""

import os
import subprocess
import sys
from pathlib import Path

from library.runtime.config import AssistantConfig


def db(cfg: AssistantConfig):
    """Seed the assistant's database by running its declared seed script."""
    section = cfg.section("db")
    if not section:
        return print("Skipping db: not declared")
    cfg.path("db").mkdir(exist_ok=True)
    seed_script = cfg.path(section["seed"])
    subprocess.run([sys.executable, str(seed_script)], check=True)


def rag(cfg: AssistantConfig):
    """Ingest the declared docs folder into the assistant's vector store."""
    section = cfg.section("rag")
    if not section:
        return print("Skipping rag: not declared")
    from library.rags.generic import Rag
    docs_dir = cfg.path(section["docs"])
    index_dir = cfg.path("db")
    count = Rag(CHROMA_DIR=str(index_dir)).ingest_directory(docs_dir)
    print(f"Ingested {count} chunks from {docs_dir} into {index_dir}")


def _api_cmd(cfg: AssistantConfig):
    """Command line that launches the declared API script."""
    api_script = cfg.path(cfg.section("api")["main"])
    return [sys.executable, str(api_script)]


def api(cfg: AssistantConfig):
    """Run the declared API in the foreground."""
    if not cfg.section("api"):
        return print("Skipping api: not declared")
    subprocess.run(_api_cmd(cfg), check=True)


def start(cfg: AssistantConfig):
    """Prepare data, start the API in the background, and run the chat UI."""
    db(cfg)
    rag(cfg)

    api_proc = None
    if cfg.section("api"):
        api_proc = subprocess.Popen(_api_cmd(cfg))

    try:
        app_script = Path(__file__).with_name("app.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_script)])
    finally:
        if api_proc:
            api_proc.terminate()


STEPS = {"db": db, "rag": rag, "api": api, "start": start}


def main():
    """Look up the requested step and run it for the assistant in WORKING_DIR."""
    if len(sys.argv) != 2 or sys.argv[1] not in STEPS:
        sys.exit(f"usage: python -m library.runtime.run <{'|'.join(STEPS)}>")

    step_name = sys.argv[1]
    step = STEPS[step_name]
    working_dir = os.environ["WORKING_DIR"]

    print(f">>> {working_dir}: running step '{step_name}'")
    cfg = AssistantConfig(working_dir)
    step(cfg)


if __name__ == "__main__":
    main()
