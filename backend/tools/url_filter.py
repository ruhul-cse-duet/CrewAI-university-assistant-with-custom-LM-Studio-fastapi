from urllib.parse import urlparse
from typing import List, Dict
import logging
from config import Config

logger = logging.getLogger(__name__)

class URLFilter:
    """
    Filter URLs to keep only official university domains
    """
    
    def __init__(self, official_domains: List[str] = None):
        # Filter out empty strings from official domains
        domains = official_domains or Config.OFFICIAL_DOMAINS
        self.official_domains = [d for d in domains if d and d.strip()]
        self.blocked_extensions = ['.pdf', '.jpg', '.png', '.gif', '.mp4', '.zip']
        
        if not self.official_domains:
            logger.warning("No official domains configured. URL filtering will be disabled.")
        
    def is_official_url(self, url: str) -> bool:
        """
        Check if URL belongs to official university domain
        """
        # If no official domains configured, allow all URLs
        if not self.official_domains:
            logger.debug("No official domains configured, allowing all URLs")
            return True
            
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix for comparison
            domain = domain.replace('www.', '')
            domain = domain.strip()
            
            # Check against official domains
            for official_domain in self.official_domains:
                if not official_domain or not official_domain.strip():
                    continue
                # Clean official domain
                clean_official = official_domain.replace('www.', '').replace('https://', '').replace('http://', '').strip()
                clean_official = clean_official.rstrip('/')
                
                if clean_official:
                    # Exact match or subdomain match
                    if domain == clean_official or domain.endswith(f'.{clean_official}'):
                        logger.debug(f"URL {url} matches official domain {clean_official}")
                        return True
            
            logger.debug(f"URL {url} (domain: {domain}) does not match any official domain")
            return False
            
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {str(e)}")
            return False
    
    def is_valid_content_type(self, url: str) -> bool:
        """
        Check if URL points to valid content (not binary files)
        """
        url_lower = url.lower()
        
        # Block binary files
        for ext in self.blocked_extensions:
            if url_lower.endswith(ext):
                return False
        
        # Allow HTML and text content
        return True
    
    def filter_search_results(self, search_results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filter search results to keep only official and valid URLs
        
        Args:
            search_results: List of dicts with 'url', 'title', 'snippet'
            
        Returns:
            Filtered list of search results
        """
        filtered = []
        
        for result in search_results:
            url = result.get('url', '')
            
            if not url:
                continue
            
            # Check if official domain
            if not self.is_official_url(url):
                logger.debug(f"Filtered out (not official): {url}")
                continue
            
            # Check if valid content type
            if not self.is_valid_content_type(url):
                logger.debug(f"Filtered out (invalid content): {url}")
                continue
            
            filtered.append(result)
        
        logger.info(f"Filtered {len(search_results)} URLs down to {len(filtered)} official URLs")
        return filtered
    
    def deduplicate_urls(self, urls: List[str]) -> List[str]:
        """
        Remove duplicate URLs (normalize and dedupe)
        """
        seen = set()
        unique = []
        
        for url in urls:
            # Normalize URL (remove trailing slash, fragments, etc.)
            normalized = url.rstrip('/').split('#')[0].split('?')[0]
            
            if normalized not in seen:
                seen.add(normalized)
                unique.append(url)
        
        logger.info(f"Deduplicated {len(urls)} URLs to {len(unique)} unique URLs")
        return unique


# Example usage
if __name__ == "__main__":
    url_filter = URLFilter()
    
    # Test URLs
    test_urls = [
        {"url": "https://www.duet.ac.bd/notice/all-notices", "title": "Notices"},
        {"url": "https://www.duet.ac.bd/event/", "title": "event"},
        {"url": "https://www.duet.ac.bd/office/central-library", "title": "central-library"},
        {"url": "https://www.duet.ac.bd/department", "title": "cse"},
    ]
    
    filtered = url_filter.filter_search_results(test_urls)
    
    print("Filtered URLs:")
    for item in filtered:
        print(f"  - {item['url']}")
