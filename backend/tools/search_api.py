import os
import requests
from typing import List, Dict, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class SearchAPI:
    """
    Google Search API Integration with fallback options
    Supports: Google Custom Search, Serper API, and DuckDuckGo
    """
    
    def __init__(self):
        #self.config = Config()
        self.serper_api_key = Config.SERPER_API_KEY
        self.google_api_key = Config.GOOGLE_SEARCH_API_KEY
        self.google_cx = Config.GOOGLE_SEARCH_ENGINE_ID
        
    def search(
        self, 
        query: str, 
        num_results: int = 10,
        site_restrict: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Search using available API (priority: Serper > Google > DuckDuckGo)
        
        Args:
            query: Search query
            num_results: Number of results to return
            site_restrict: Restrict to specific domain
            
        Returns:
            List of search results with title, url, snippet
        """
        try:
            # Add site restriction if provided
            if site_restrict:
                query = f"site:{site_restrict} {query}"
            
            # Try Serper API first (more generous free tier)
            if self.serper_api_key:
                return self._search_serper(query, num_results)
            
            # Fallback to Google Custom Search
            elif self.google_api_key and self.google_cx:
                return self._search_google(query, num_results)
            
            # Fallback to DuckDuckGo (no API key needed)
            else:
                logger.warning("No API key found, using DuckDuckGo fallback")
                return self._search_duckduckgo(query, num_results)
                
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def _search_serper(self, query: str, num: int) -> List[Dict[str, str]]:
        """Search using Serper API (https://serper.dev)"""
        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": num,
                "gl": "bd",  # Bangladesh
                "hl": "bn"   # Bengali
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=400)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic", [])[:num]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "date": item.get("date", "")
                })
            
            logger.info(f"Serper API returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Serper API error: {str(e)}")
            raise
    
    def _search_google(self, query: str, num: int) -> List[Dict[str, str]]:
        """Search using Google Custom Search API"""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cx,
                "q": query,
                "num": min(num, 10),  # Google API max is 10
                "gl": "bd",
                "lr": "lang_bn|lang_en"
            }
            
            response = requests.get(url, params=params, timeout=300)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("items", [])[:num]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "date": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", "")
                })
            
            logger.info(f"Google API returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Google API error: {str(e)}")
            raise
    
    def _search_duckduckgo(self, query: str, num: int) -> List[Dict[str, str]]:
        """Search using DuckDuckGo (no API key needed)"""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=num)
                for item in search_results:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", ""),
                        "date": ""
                    })
            
            logger.info(f"DuckDuckGo returned {len(results)} results")
            return results
            
        except ImportError:
            logger.error("duckduckgo-search package not installed")
            return []
        except Exception as e:
            logger.error(f"DuckDuckGo error: {str(e)}")
            return []
    
    def search_university(self, query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """
        Search specifically within university domain
        """
        try:
            # Use query as-is (already enhanced in router)
            site_restrict = Config.UNIVERSITY_DOMAIN if Config.UNIVERSITY_DOMAIN else None
            
            logger.info(f"Searching university: query='{query}', domain='{site_restrict}'")
            
            results = self.search(
                query, 
                num_results, 
                site_restrict=site_restrict
            )
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in search_university: {str(e)}", exc_info=True)
            return []

search_api = SearchAPI()
# Example usage
if __name__ == "__main__":
    search_api = SearchAPI()
    
    # Test search
    results = search_api.search_university("latest notice", num_results=5)
    
    for idx, result in enumerate(results, 1):
        print(f"\n{idx}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Snippet: {result['snippet'][:100]}...")
