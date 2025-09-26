# rag_agent.py

import os
import glob
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
import shutil
import tiktoken  # Add to top of file with other imports

# === Load .env ===
load_dotenv()

# === Load environment variables ===
AZURE_OPENAI_API_KEY_SWEDEN = os.getenv("AZURE_OPENAI_API_KEY_SWEDEN")
AZURE_OPENAI_ENDPOINT_SWEDEN = os.getenv("AZURE_OPENAI_ENDPOINT_SWEDEN")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")

# Set Azure OpenAI config
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY_SWEDEN
os.environ["OPENAI_API_VERSION"] = AZURE_OPENAI_API_VERSION

# Remove conflicting base setting for newer SDKs
os.environ.pop("OPENAI_API_BASE", None)

# DEBUG print
print(f"Using endpoint: '{AZURE_OPENAI_ENDPOINT_SWEDEN}'")
print(f"Using embedding deployment: '{AZURE_OPENAI_EMBEDDING_DEPLOYMENT}'")
print(f"Chroma DB dir: '{CHROMA_DB_DIR}'")

# Use modern AzureOpenAIEmbeddings init
embedding_model = AzureOpenAIEmbeddings(
    azure_endpoint=AZURE_OPENAI_ENDPOINT_SWEDEN,
    deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    model_kwargs={},
)

# === Load and chunk documents ===
def load_and_split_documents(pdf_dir="/home/azureuser/LibreChat/uploads"):
    docs = []
    files = glob.glob(os.path.join(pdf_dir, "*.pdf"))

    print(f"📂 Found {len(files)} PDF(s) in '{pdf_dir}'")
    if files:
        print("📄 PDF files found:")
        for f in files:
            print(f"  • {os.path.basename(f)}")

    total_pages = 0
    for pdf_path in files:
        loader = PyPDFLoader(pdf_path)
        raw_pages = loader.load()
        total_pages += len(raw_pages)
        for page in raw_pages:
            page.metadata["source"] = os.path.basename(pdf_path)
            if "page" in page.metadata:
                page.metadata["page"] = int(page.metadata["page"]) + 1  # Convert to 1-based
        docs.extend(raw_pages)

    if not docs:
        print("[WARN] No documents loaded. Check PDF contents.")
    else:
        print(f"📄 Loaded {total_pages} pages from {len(files)} PDF(s)")

    # Chunking parameters
    chunk_size = 1000
    chunk_overlap = 100

    print(f"✂️ Splitting documents: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)

    print(f"🧩 Created {len(chunks)} document chunks.\n")
    return chunks


# === Create new vector DB ===
def setup_vector_store(docs, batch_size=200, max_tokens_per_minute=500_000):
    total_chunks = len(docs)
    print(f"🚀 Starting ingestion of {total_chunks} chunks in batches of {batch_size}...")

    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    tokens_used = 0
    start_time = time.time()

    vectordb = None
    for i in range(0, total_chunks, batch_size):
        batch = docs[i:i + batch_size]

        # === Calculate token count for this batch ===
        batch_tokens = sum(len(encoding.encode(doc.page_content)) for doc in batch)

        # === Rate limit handling ===
        elapsed = time.time() - start_time
        if tokens_used + batch_tokens > max_tokens_per_minute:
            sleep_time = max(60 - elapsed, 0)
            print(f"⏳ Sleeping for {sleep_time:.1f} seconds to respect token rate limit ({tokens_used + batch_tokens} > {max_tokens_per_minute})...")
            time.sleep(sleep_time)
            tokens_used = 0
            start_time = time.time()

        # === Ingest batch ===
        if vectordb is None:
            vectordb = Chroma.from_documents(
                documents=batch,
                embedding=embedding_model,
                persist_directory=CHROMA_DB_DIR
            )
        else:
            vectordb.add_documents(batch)

        tokens_used += batch_tokens
        print(f"✅ Ingested batch {i // batch_size + 1} ({len(batch)} chunks, {batch_tokens} tokens)")

    print("✅ Vector store ingestion complete.\n")
    return vectordb


# === Load existing vector DB ===
def load_vector_store():
    return Chroma(
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_DIR
    )


def list_pdf_files_from_vector_store():
    vectordb = load_vector_store()
    collection = vectordb.get()
    file_page_counts = {}

    for metadata in collection['metadatas']:
        source = metadata.get("source", "Unknown file")
        page = metadata.get("page", None)
        if page is not None:
            try:
                page = int(page)
            except:
                continue
            if source not in file_page_counts:
                file_page_counts[source] = set()
            file_page_counts[source].add(page)

    return {
        fname: len(pages)
        for fname, pages in file_page_counts.items()
    }


# === Build RetrievalQA chain ===
def get_qa_chain(filter_by_source: str = None):
    vectorstore = load_vector_store()

    search_kwargs = {"k": 5}  # bump k
    if filter_by_source:
        search_kwargs["filter"] = {"source": filter_by_source}

    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    llm = AzureChatOpenAI(
        deployment_name="gpt-4o",
        model="gpt-4o",
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT_SWEDEN,
        api_key=AZURE_OPENAI_API_KEY_SWEDEN,
        max_tokens=1024,
        temperature=0.2,
    )

    return RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True
    )


# === Ingest documents (optional, can skip if already done) ===
def ingest_documents():
    docs = load_and_split_documents()
    if not docs:
        raise ValueError("No documents found to ingest.")
    print(f"Ingesting {len(docs)} document chunks into vector store...")
    setup_vector_store(docs)
    print("Ingestion complete.")
