from dotenv import load_dotenv
from library.rags.generic import Rag
from pathlib import Path
import os

WORKING_DIR = os.environ.get("WORKING_DIR")
load_dotenv(f"{WORKING_DIR}/.env")

APP_KEY = os.environ.get("APP_KEY")
APP_NAME = os.environ.get("APP_NAME")
DB_PATH = Path(f"{WORKING_DIR}/db")

rag = Rag(
    CHROMA_DIR=f"{DB_PATH}"
)

if __name__ == "__main__":
    DOCS_DIR = Path(f"{WORKING_DIR}/resources/docs")
    count = rag.ingest_directory(DOCS_DIR)
    print(f"Ingested {count} chunks from {DOCS_DIR} into {DB_PATH}")