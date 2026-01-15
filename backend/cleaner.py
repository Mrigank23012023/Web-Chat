import logging
import re

logger = logging.getLogger(__name__)

class Cleaner:
    """Normalizes text for processing."""
    
    def clean(self, text: str) -> str:
        """
        Cleans and normalizes the input text.
        
        Args:
            text (str): Raw text.
            
        Returns:
            str: Cleaned text.
        """
        if not text:
            return ""
            
        # 1. Normalize line breaks (Windows/Classic Mac to Unix)
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 2. Collapse more than 2 newlines into 2 (Preserves paragraphs)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 3. Collapse multiple horizontal spaces/tabs into one space
        # (This avoids destroying the indentation if we simply used \s+)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 4. Strip leading/trailing whitespace
        return text.strip()
