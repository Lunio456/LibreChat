# server.py

from mcp.server.fastmcp import FastMCP
from rag_agent import ingest_documents, get_qa_chain
import logging

logger = logging.getLogger(__name__)

mcp = FastMCP("rag_agent")

# Try to ingest documents and load the chain on server startup
try:
    ingest_documents()
except Exception as e:
    logger.warning(f"[WARN] Document ingestion skipped or failed: {e}")

qa_chain = get_qa_chain()

@mcp.tool()
async def query_kpi(query: str) -> str:
    """Extract KPI information from embedded annual reports."""
    try:
        result = qa_chain({"query": query})
        answer = result['answer']
        sources = result.get("source_documents", [])

        source_info = ""
        for doc in sources:
            metadata = doc.metadata
            source = metadata.get("source", "Unknown file")
            page = metadata.get("page", "Unknown page")
            source_info += f"- File: {source}, Page: {page}\n"

        return f"{answer}\n\n📄 Sources:\n{source_info.strip()}"
    except Exception as e:
        return f"[ERROR] Failed to query documents: {e}"

def main():
    mcp.run(transport="stdio")
