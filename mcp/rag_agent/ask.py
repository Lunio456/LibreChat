from rag_agent import get_qa_chain, list_pdf_files_from_vector_store

def main():
    file_info = list_pdf_files_from_vector_store()
    total_pages = sum(file_info.values())
    print("📚 Files loaded and available for querying:")
    for fname, page_count in file_info.items():
        print(f"  - {fname} ({page_count} pages)")
    print(f"Total pages loaded across all PDFs: {total_pages}")

    print("\nAsk a question about the PDFs. Type 'exit' to quit.")

    while True:
        question = input("Q: ").strip()
        if question.lower() in ("exit", "quit"):
            break

        # Optional: detect which file the question targets
        filter_file = None
        for fname in file_info:
            if fname.lower() in question.lower():
                filter_file = fname
                break

        # Get the appropriate Retrieval QA chain
        qa_chain = get_qa_chain(filter_by_source=filter_file)

        # Ask the question
        result = qa_chain.invoke({"question": question})

        print(f"\nA: {result.get('answer', '').strip()}\n")

        # 📄 Show deduplicated sources with 1-based page numbers
        source_docs = result.get("source_documents", [])
        if source_docs:
            unique_sources = {
                f"- File: {doc.metadata.get('source', 'Unknown')}, Page: {int(doc.metadata.get('page', 0)) + 1}"
                for doc in source_docs
            }
            print("📄 Sources:")
            for source in sorted(unique_sources):
                print(source)

if __name__ == "__main__":
    main()
