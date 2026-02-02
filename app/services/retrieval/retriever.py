from typing import List, Dict, Any
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings, logger

class PineconeRetriever:
    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        
        # Initialize VectorStore
        if self.api_key and self.index_name:
            self.vectorstore = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embeddings,
                pinecone_api_key=self.api_key
            )
        else:
            self.vectorstore = None
            logger.warning("PINECONE_API_KEY or PINECONE_INDEX_NAME not found in settings.")

    def retrieve(self, query: str, container_tag: str = None, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Query Pinecone knowledge base. 
        Filters by 'knowledge_base_type' in metadata if container_tag is provided.
        """
        if not self.vectorstore:
            logger.error("Pinecone VectorStore not initialized.")
            return []

        filter_dict = {}
        if container_tag:
            filter_dict = {"knowledge_base_type": container_tag}

        try:
            docs = self.vectorstore.similarity_search(
                query, 
                k=top_k,
                filter=filter_dict if filter_dict else None
            )
            
            processed_results = []
            for doc in docs:
                processed_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            return processed_results
        except Exception as e:
            logger.error(f"Pinecone Search Exception: {str(e)}")
            return []

    def add_learned_knowledge(self, content: str, source_url: str, intent: str):
        """
        Upserts newly discovered knowledge into Pinecone.
        """
        if not self.vectorstore:
            return
            
        metadata = {
            "document_name": "Web Search (Learned)",
            "source_url": source_url,
            "knowledge_base_type": intent,
            "is_learned": True
        }
        
        try:
            self.vectorstore.add_texts(
                texts=[content],
                metadatas=[metadata]
            )
            logger.info(f"Learned new information for {intent}")
        except Exception as e:
            logger.error(f"Error learning knowledge: {e}")

def get_hybrid_context(query: str) -> str:
    """Combines context from both disease and scheme tags."""
    retriever = PineconeRetriever()
    disease_chunks = retriever.retrieve(query, container_tag="disease", top_k=3)
    scheme_chunks = retriever.retrieve(query, container_tag="scheme", top_k=3)
    
    # Format for LLM
    context = "DISEASE KNOWLEDGE BASE:\n"
    for chunk in disease_chunks:
        context += f"- {chunk.get('content')} (Source: {chunk.get('metadata', {}).get('document_name')}, Page: {chunk.get('metadata', {}).get('page_number')})\n"
    
    context += "\nGOVERNMENT SCHEMES KNOWLEDGE BASE:\n"
    for chunk in scheme_chunks:
        context += f"- {chunk.get('content')} (Source: {chunk.get('metadata', {}).get('document_name')}, Page: {chunk.get('metadata', {}).get('page_number')})\n"
        
    return context

if __name__ == "__main__":
    # Standard test block
    retriever = PineconeRetriever()
    results = retriever.retrieve("Citrus Canker prevention", container_tag="disease")
    for r in results:
        logger.info(f"Found: {r.get('content')[:100]}...")
