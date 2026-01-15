import logging
from typing import List

logger = logging.getLogger(__name__)

class Retriever:
    """Retrieves relevant context based on queries."""
    
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Finds relevant chunks for the query.
        
        Args:
            query (str): User question.
            top_k (int): Number of chunks to retrieve.
            
        Returns:
            List[str]: Retrieved text chunks.
        """
        if not query:
            return []
            
        logger.info(f"Retrieving top {top_k} results for query: {query}")
        return []
