import logging
from typing import List, Dict, Any
# Phase 6 Fix: Standard import path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import Config

logger = logging.getLogger(__name__)

class Chunker:
    """Splits text into semantic chunks."""
    
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""] # Standard hierarchy for semantic splitting
        )
    
    def chunk(self, text: str, source_url: str, title: str = "Unknown") -> List[Document]:
        """
        Splits the text into chunks associated with the source URL.
        
        Args:
            text (str): The clean text to split.
            source_url (str): The source URL for metadata.
            title (str): Title of the page.
            
        Returns:
            List[Document]: A list of LangChain Document objects.
        """
        if not text:
            logger.warning("Attempted to chunk empty text.")
            return []
            
        metadata = {"source": source_url, "title": title} 
        
        chunks = self.splitter.create_documents([text], metadatas=[metadata])
        
        # Phase 6 Fix: Filter empty chunks just in case
        chunks = [c for c in chunks if c.page_content and c.page_content.strip()]
        
        logger.info(f"Split text into {len(chunks)} chunks for {source_url}.")
        return chunks
