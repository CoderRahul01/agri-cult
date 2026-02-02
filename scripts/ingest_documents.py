import os
import argparse
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CHUNKING_PARAMS = {
    "chunk_size": 1000,  # Standard chunks for Pinecone
    "chunk_overlap": 100
}

DATA_DIR = "data"

# Mapping files to knowledge base types
PDF_FILES = {
    "CitrusPlantPestsAndDiseases.pdf": "disease",
    "GovernmentSchemes.pdf": "scheme"
}

def ingest_to_pinecone():
    print("🚀 Starting Pinecone ingestion pipeline...")

    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not api_key or not index_name:
        print("❌ Error: PINECONE_API_KEY or PINECONE_INDEX_NAME not found in environment variables.")
        return

    # Initialize embeddings (1024 dimensions to match index)
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNKING_PARAMS["chunk_size"],
        chunk_overlap=CHUNKING_PARAMS["chunk_overlap"]
    )

    all_docs = []

    for filename, kb_type in PDF_FILES.items():
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            print(f"⚠️ Warning: {file_path} not found. Skipping...")
            continue

        print(f"📄 Processing {filename} ({kb_type})...")

        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split documents
        chunks = text_splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata.update({
                "document_name": filename,
                "page_number": chunk.metadata.get("page", 0) + 1,
                "knowledge_base_type": kb_type
            })
            all_docs.append(chunk)

    if not all_docs:
        print("⚠️ No documents found to ingest.")
        return

    print(f"✨ Sending {len(all_docs)} chunks to Pinecone index: {index_name}...")

    try:
        PineconeVectorStore.from_documents(
            all_docs,
            embeddings,
            index_name=index_name,
            pinecone_api_key=api_key
        )
        print("✅ Pinecone ingestion completed successfully.")
    except Exception as e:
        print(f"❌ Exception during upload: {str(e)}")

if __name__ == "__main__":
    ingest_to_pinecone()
