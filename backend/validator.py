import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Validator:
    """Validates user inputs and URLs to prevent injection or invalid processing."""
    
    @staticmethod
    def validate_gateway(url: str) -> dict:
        """
        Validates the URL format and accessibility.
        
        Args:
            url (str): The URL to validate.
            
        Returns:
            dict: {"valid": bool, "error": Optional[str]}
        """
        # 1. Format Validation
        if not url:
            return {"valid": False, "error": "URL cannot be empty."}
            
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                 return {"valid": False, "error": "Invalid URL format. Scheme (http/https) or domain missing."}
        except Exception:
            return {"valid": False, "error": "Malformed URL."}

        # 2. Network Reachability Validation
        try:
            from config import Config
            import requests

            headers = {"User-Agent": Config.USER_AGENT}
            response = requests.get(url, timeout=Config.REQUEST_TIMEOUT, headers=headers)
            
            # Status Code Check
            if response.status_code != 200:
                return {
                    "valid": False, 
                    "error": f"Website unreachable. Status Code: {response.status_code}"
                }
            
            # Content Type Check
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type:
                logger.warning(f"Invalid Content-Type for {url}: {content_type}")
                return {
                    "valid": False, 
                    "error": f"URL does not point to a website (Content-Type: {content_type}). Expecting text/html."
                }
                
            return {"valid": True, "error": None}

        except requests.Timeout:
            return {"valid": False, "error": f"Connection timed out (Limit: {Config.REQUEST_TIMEOUT}s)."}
        except requests.exceptions.SSLError:
            logger.error(f"SSL Error for {url}")
            return {"valid": False, "error": "SSL Certificate verification failed. The website might be insecure."}
        except requests.exceptions.TooManyRedirects:
            logger.error(f"Redirect loop for {url}")
            return {"valid": False, "error": "Too many redirects. The website is looping."}
        except requests.RequestException as e:
            logger.error(f"Validation error for {url}: {e}")
            return {"valid": False, "error": f"Connection failed: {str(e)}"}
