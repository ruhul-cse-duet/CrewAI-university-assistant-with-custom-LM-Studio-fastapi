from tools.custom_tool import tool
from typing import Dict
import logging
from tools.search_api import SearchAPI
from tools.url_filter import URLFilter
from tools.scraper import WebScraper
from tools.faiss_store import FAISSStore

logger = logging.getLogger(__name__)

# Initialize tools
search_api = SearchAPI()
url_filter = URLFilter()
scraper = WebScraper()
faiss_db = FAISSStore()

@tool(
    name="University Hybrid Search",
    description="""Search university website using hybrid semantic + keyword search.
    Performs Google/Serper search, filters official URLs, scrapes content,
    generates embeddings, stores in FAISS, and performs semantic search."""
)
def university_hybrid_search(query: str) -> str:
    """
    Complete hybrid search pipeline for university information.
    
    Steps:
    1. Google/Serper search for relevant pages
    2. Filter to keep only official university URLs
    3. Scrape and clean page content
    4. Generate embeddings and store in FAISS
    5. Perform semantic search to find most relevant content
    
    Args:
        query: The search query from the student
        
    Returns:
        String containing the most relevant information found
    """
    try:
        logger.info(f"Hybrid search for query: {query}")
        
        # Step 1: Search Google/Serper
        logger.info("Step 1: Searching...")
        search_results = search_api.search_university(query, num_results=10)
        
        if not search_results:
            return "No search results found. Please try a different query."
        
        logger.info(f"Found {len(search_results)} search results")
        
        # Step 2: Filter to official URLs
        logger.info("Step 2: Filtering official URLs...")
        official_results = url_filter.filter_search_results(search_results)
        
        if not official_results:
            return "No official university pages found for this query."
        
        logger.info(f"Filtered to {len(official_results)} official URLs")
        
        # Step 3: Scrape pages
        logger.info("Step 3: Scraping pages...")
        documents = []
        for result in official_results[:5]:  # Limit to top 5
            scraped = scraper.scrape_url(result['url'])
            if scraped and scraped.get('content'):
                documents.append(scraped)
        
        if not documents:
            return "Could not extract content from university pages."
        
        logger.info(f"Successfully scraped {len(documents)} documents")
        
        # Step 4: Store in FAISS
        logger.info("Step 4: Adding to FAISS...")
        faiss_db.add_documents(documents)
        
        # Step 5: Semantic search
        logger.info("Step 5: Performing semantic search...")
        results = faiss_db.search(query, top_k=3, threshold=0.5)
        
        if not results:
            return "No relevant information found in the scraped content."
        
        # Format results
        formatted_results = []
        for idx, result in enumerate(results, 1):
            formatted_results.append(
                f"[Source {idx}]\n"
                f"Title: {result.get('title', 'N/A')}\n"
                f"URL: {result.get('url', 'N/A')}\n"
                f"Relevance: {result.get('score', 0):.2f}\n"
                f"Content:\n{result.get('preview', '')}\n"
            )
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Error in hybrid search: {str(e)}", exc_info=True)
        return f"Error performing search: {str(e)}"
