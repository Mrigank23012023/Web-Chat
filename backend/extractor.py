import logging
import trafilatura
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class Extractor:
    """Extracts main content and metadata from HTML."""
    
    def extract(self, html_content: str) -> Dict[str, Optional[str]]:
        """
        Extracts text content and title from HTML.
        
        Args:
            html_content (str): Raw HTML content.
            
        Returns:
            Dict: {"text": str, "title": str} or None if failed.
        """
        if not html_content:
            logger.warning("Empty HTML content provided for extraction.")
            return None
            
        try:
            # Phase 5 Improvement: Use bare_extraction to get metadata (Title)
            data = trafilatura.bare_extraction(
                html_content, 
                include_comments=False, 
                include_tables=True,
                no_fallback=True
            )
            
            if not data or not data.get('text'):
                logger.warning("Extraction returned empty data.")
                return None
            
            text = data['text']
            title = data.get('title', 'Unknown Title')
            
            # Phase 5 Fix: Whitespace Normalization
            text = text.replace('\xa0', ' ')
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            # Minimum content filter
            if len(text) < 50:
                logger.warning(f"Extracted content too short ({len(text)} chars). Skipping.")
                return None
            
            # Diagnostics
            compression_ratio = len(text) / len(html_content) if len(html_content) > 0 else 0
            logger.info(f"Extraction successful. Size: {len(text)} chars (Ratio: {compression_ratio:.2f})")
                
            return {"text": text, "title": title}
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return None
