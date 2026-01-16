import logging
import chromadb
import os
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone
from config import Config

logger = logging.getLogger(__name__)

class VectorStore:
    
    def __init__(self, collection_name: str = "website_content"):
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        
        self.collection_name = collection_name
        self.provider = Config.VECTOR_STORE_PROVIDER
        
        if self.provider == "chroma":
            self.persist_directory = Config.CHROMA_DB_PATH
            try:
                # Initialize client explicitly for better control
                self.client = chromadb.PersistentClient(path=self.persist_directory)
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB client: {e}")
                raise e
        elif self.provider == "pinecone":
            self.index_name = Config.PINECONE_INDEX_NAME
            if not Config.PINECONE_API_KEY:
                raise ValueError("Pinecone API Key is missing.")
    
    def _reset_collection(self):
        try:
            logger.info(f"Resetting vector store ({self.provider})...")
            
            if self.provider == "chroma":
                try:
                    self.client.delete_collection(name=self.collection_name)
                    logger.info(f"Deleted existing Chroma collection '{self.collection_name}'.")
                except ValueError:
                    # Collection might not exist, which is fine
                    pass 
                    
            elif self.provider == "pinecone":
                try:
                    pc = Pinecone(api_key=Config.PINECONE_API_KEY)
                    index = pc.Index(self.index_name)
                    index.delete(delete_all=True)
                    logger.info(f"Cleared Pinecone index '{self.index_name}'.")
                except Exception as e:
                    if "NOT_FOUND" in str(e) or "404" in str(e):
                        logger.warning(f"Index '{self.index_name}' does not exist yet. Skipping reset.")
                    else:
                        logger.error(f"Failed to reset Pinecone index: {e}")
                        raise RuntimeError("Could not reset Pinecone index.")

        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            raise RuntimeError(f"Could not reset vector store for new site: {e}")

    def create_collection(self, documents: List[Document], embedding_function):
        if not documents:
            logger.warning("No documents provided to create collection.")
            return None
            
        logger.info(f"Creating vector store ({self.provider}) with {len(documents)} documents.")
        
        self._reset_collection()
        
        if self.provider == "chroma":
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embedding_function,
                collection_name=self.collection_name,
                client=self.client
            )
        elif self.provider == "pinecone":
            vectorstore = PineconeVectorStore.from_documents(
                documents=documents,
                embedding=embedding_function,
                index_name=self.index_name,
                pinecone_api_key=Config.PINECONE_API_KEY
            )
        
        logger.info("Vector store created and persisted.")
        return vectorstore

    def as_retriever(self, vectorstore):
        return vectorstore.as_retriever(search_kwargs={"k": Config.RETRIEVAL_TOP_K})
