"""RAG tool for searching an assistant's local documents (policies, product
terms, correspondence notes, etc.).

Separate from the MCP sqlite tools since this is a local vector search
concern, not a database-server one. Each assistant instantiates its own
Rag(CHROMA_DIR=...) in resources/rag.py; call .get_tools() from the
assistant's Router.get_tools() to make search_correspondence available to
the agent, and .ingest_directory(docs_dir) to (re)index a folder of .md/.pdf
files — resources/rag.py does both when run directly via `make rag`.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

class Rag:

    def __init__(self, CHROMA_DIR: str, EMBEDDING_MODEL: str = "qwen3-embedding"):
        self.CHROMA_DIR = CHROMA_DIR
        self.EMBEDDING_MODEL = EMBEDDING_MODEL
        self.STORE = self.create_store()
        # Built as a closure over self.STORE (rather than a @tool-decorated
        # method) so the tool's schema only ever exposes `query` — a @tool
        # on an instance method bakes `self` into the schema as a required
        # arg, since StructuredTool objects don't go through Python's normal
        # method-binding descriptor protocol.
        self.search_correspondence = self._build_search_tool()

    def create_store(self):
        _store = Chroma(
            persist_directory=str(self.CHROMA_DIR),
            embedding_function=OllamaEmbeddings(model=self.EMBEDDING_MODEL),
        )
        return _store

    def _build_search_tool(self):
        store = self.STORE

        @tool
        def search_correspondence(query: str) -> str:
            """Search local policies, product terms, and customer/supplier
            correspondence notes (e.g. agreed payment terms, delivery
            arrangements, discounts, hardship/dispute case notes). Not for
            structured data like balances, invoice amounts, or loan/order
            status — use the SQL tools for that."""

            results = store.similarity_search(query, k=3)

            if not results:
                return f"No documents found matching '{query}'."
            return "\n\n".join(
                f"[{r.metadata.get('doc_type', 'document')}] "
                f"{r.metadata.get('title', r.metadata.get('source', 'untitled'))}\n"
                f"{r.page_content}"
                for r in results
            )
        return search_correspondence

    def get_tools(self) -> list:
        return [self.search_correspondence]

    def ingest_directory(self, docs_dir: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> int:
        """(Re)index every .md/.pdf file in docs_dir into the vector store.
        Chunk ids are derived from filename + chunk index, so re-running
        upserts rather than duplicating — safe to repeat, same as seed_data.py."""

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks, ids = [], []

        for path in sorted(Path(docs_dir).glob("*")):
            if path.suffix == ".md":
                text = path.read_text(encoding="utf-8")
            elif path.suffix == ".pdf":
                text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
            else:
                continue

            metadata = {
                "source": path.name,
                "title": self._extract_title(text, path),
                "doc_type": self._extract_doc_type(text),
            }
            for i, chunk in enumerate(splitter.split_text(text)):
                chunks.append(Document(page_content=chunk, metadata=metadata))
                ids.append(f"{path.name}::{i}")

        if not chunks:
            return 0
        self.STORE.add_documents(chunks, ids=ids)
        return len(chunks)

    @staticmethod
    def _extract_title(text: str, path: Path) -> str:
        for line in text.splitlines():
            line = line.strip().lstrip("#").strip()
            if line:
                return line[:80]
        return path.stem

    @staticmethod
    def _extract_doc_type(text: str) -> str:
        for line in text.splitlines()[:10]:
            stripped = line.replace("*", "").strip()
            if stripped.lower().startswith("document type:"):
                return stripped.split(":", 1)[1].strip()
        return "document"


# testing code
if __name__ == '__main__':

    rag = Rag(
        CHROMA_DIR="db/temp"
    )