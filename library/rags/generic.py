"""RAG tool for searching fake customer/supplier correspondence.

Separate from the MCP sqlite tools since this is a local vector search
concern, not a database-server one. Import search_correspondence and add it
to whichever agent(s)/subagent(s) need it.
"""

from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings

class Rag:

    def __init__(self, CHROMA_DIR: str, EMBEDDING_MODEL: str = "qwen3-embedding"):
        self.CHROMA_DIR = CHROMA_DIR
        self.EMBEDDING_MODEL = EMBEDDING_MODEL
        self.STORE = self.create_store()

    def create_store(self):
        _store = Chroma(
            persist_directory=str(self.CHROMA_DIR),
            embedding_function=OllamaEmbeddings(model=self.EMBEDDING_MODEL),
        )
        return _store

    @tool
    def search_correspondence(self,query: str) -> str:
        """Search past correspondence, contracts, and notes about customers and
        suppliers (e.g. agreed payment terms, delivery arrangements, discounts).
        Not for structured data like invoice amounts or order status — use the
        SQL tools for that."""

        results = self.STORE.similarity_search(query, k=3)

        if not results:
            return f"No correspondence found matching '{query}'."
        return "\n\n".join(
            f"[{r.metadata['entity_type']}: {r.metadata['entity_name']}] "
            f"{r.metadata['title']} ({r.metadata['date']})\n{r.page_content}"
            for r in results
        )


# testing code
if __name__ == '__main__':

    rag = Rag(
        CHROMA_DIR="db/temp"
    )