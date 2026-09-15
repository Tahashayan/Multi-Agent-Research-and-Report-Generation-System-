import os
import json
import re
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Define folder paths (anchored to this script's location, so it works
#    no matter which directory you run the script from)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "..", "pdfs")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "..", "chunks")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "perfect_chunks.json")

def clean_text(text: str) -> str:
    """Removes weird PDF formatting like extra spaces, newlines, and page numbers."""
    # Replace multiple newlines with a single space
    text = re.sub(r'\n+', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_pdfs():
    print(f"📂 Loading PDFs from {PDF_FOLDER}...")

    # 2. Load all PDFs from the directory
    loader = PyPDFDirectoryLoader(PDF_FOLDER)
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} pages in total.")

    # 3. Configure the Smart Splitter
    # 2000 characters is roughly 300-450 words.
    # chunk_overlap=0 ensures we don't have duplicate text in our training data.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=0,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]  # Splits by paragraph first, then sentence
    )

    print("✂️ Chunking text...")
    chunks = text_splitter.split_documents(documents)

    final_chunks = []

    # 4. Clean and filter the chunks
    for chunk in chunks:
        clean_chunk = clean_text(chunk.page_content)

        # Throw away junk chunks (like page numbers, short table of contents, or headers)
        # We only want meaty paragraphs (minimum 500 characters / ~100 words)
        if len(clean_chunk) > 500:
            final_chunks.append({
                "source": chunk.metadata.get("source", "unknown"),
                "page": chunk.metadata.get("page", 0),
                "text": clean_chunk
            })

    print(f"✅ Created {len(final_chunks)} perfect, clean text chunks.")

    # 5. Save the chunks to a JSON file so we can use them in Step 1.3
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=4, ensure_ascii=False)

    print(f"💾 Saved successfully to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_pdfs()