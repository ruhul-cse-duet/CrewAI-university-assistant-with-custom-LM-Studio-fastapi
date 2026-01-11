import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging
import re
from config import Config

logger = logging.getLogger(__name__)


class WebScraper:
    """
    Advanced web scraper with text cleaning and extraction
    """
    
    def __init__(self, timeout=120, max_length=5000):
        self.timeout = timeout
        self.max_length = max_length
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
            'Accept-Encoding': 'gzip, deflate'  # Don't request brotli to avoid decoding issues
        }
        logger.info(f"Initialized WebScraper (timeout={timeout}s, max_length={max_length})")
    
    def scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape and clean content from URL
        
        Returns:
            Dict with 'url', 'title', 'content', 'date'
        """
        try:
            logger.info(f"Scraping: {url}")
            
            # Fetch page
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout,
                verify=True
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract and clean content
            content = self._extract_content(soup)
            
            # Extract date if available
            date = self._extract_date(soup)
            
            if not content or len(content.strip()) < 50:
                logger.warning(f"No meaningful content extracted from {url} (got {len(content)} chars)")
                return None
            
            # Limit content length
            if len(content) > self.max_length:
                content = content[:self.max_length] + "..."
                logger.info(f"Content truncated to {self.max_length} chars")
            
            logger.info(f"Successfully scraped: {title} ({len(content)} chars)")
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'date': date
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout scraping {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error scraping {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try meta tags first
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title['content'].strip()
        
        # Try regular title tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try h1 tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Untitled"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract and clean main content"""
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                             'aside', 'iframe', 'noscript', 'meta', 'link']):
            element.decompose()
        
        # Try to find main content area
        main_content = None
        
        # Try common content selectors
        for selector in ['main', 'article', '.content', '.main-content', 
                        '#content', '#main', '.post-content', '.entry-content']:
            main_content = soup.select_one(selector)
            if main_content:
                logger.debug(f"Found content in: {selector}")
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')
            logger.debug("Using body as content source")
        
        if not main_content:
            logger.warning("No content area found")
            return ""
        
        # Extract text
        text = main_content.get_text(separator='\n', strip=True)
        
        # Clean text
        text = self._clean_text(text)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        
        # Remove extra whitespace
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\t+', ' ', text)
        
        # Remove very short lines (likely navigation/junk)
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            # Keep lines that are either:
            # - More than 20 chars, OR
            # - Look like headers (short but meaningful)
            if len(line) > 20 or (len(line) > 0 and line[0].isupper()):
                lines.append(line)
        
        text = '\n'.join(lines)
        
        return text.strip()
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract publication/update date"""
        # Try meta tags
        for meta in ['article:published_time', 'article:modified_time', 'datePublished', 'dateModified']:
            meta_tag = soup.find('meta', property=meta) or soup.find('meta', {'name': meta})
            if meta_tag and meta_tag.get('content'):
                return meta_tag['content']
        
        # Try time tag
        time_tag = soup.find('time')
        if time_tag:
            if time_tag.get('datetime'):
                return time_tag['datetime']
            return time_tag.get_text().strip()
        
        # Try common date classes
        for class_pattern in ['date', 'time', 'published', 'post-date', 'entry-date']:
            date_elem = soup.find(class_=re.compile(class_pattern, re.I))
            if date_elem:
                return date_elem.get_text().strip()
        
        return ""
    
    # Backward compatibility alias
    def scrape(self, url: str) -> Optional[str]:
        """Backward compatible method - returns just content text"""
        result = self.scrape_url(url)
        return result['content'] if result else None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = WebScraper()
    
    test_url = ""
    result = scraper.scrape_url(test_url)
    
    if result:
        print(f"\nTitle: {result['title']}")
        print(f"Date: {result['date']}")
        print(f"Content length: {len(result['content'])} chars")
        print(f"\nPreview:\n{result['content'][:300]}...")
    else:
        print("Scraping failed!")
