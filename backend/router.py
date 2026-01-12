from typing import Dict, List, Optional
import logging
from tools.search_api import SearchAPI
from tools.url_filter import URLFilter
from tools.scraper import WebScraper
from tools.faiss_store import FAISSStore
from llm import get_llm
from config import Config

logger = logging.getLogger(__name__)

class QueryRouter:
    """
    Smart Router following the workflow:
    1. Student Question
    2. Select Agent (Notice/Faculty/Library)
    3. Search Google
    4. Filter URLs (official only)
    5. Scrape & Clean
    6. Store in FAISS
    7. Semantic Search
    8. Generate Answer with LLM
    """
    
    def __init__(self, faiss_store=None):
        logger.info("Initializing QueryRouter components...")
        self.search_api = SearchAPI()
        self.url_filter = URLFilter()
        self.scraper = WebScraper()
        # Use provided FAISS store or create new one
        if faiss_store:
            self.faiss_store = faiss_store
        else:
            try:
                self.faiss_store = FAISSStore()
            except Exception as e:
                logger.error(f"Failed to initialize FAISS store: {str(e)}")
                self.faiss_store = None
        self.llm = get_llm()
        
        # Agent classification keywords
        self.agent_keywords = {
            'notice': ['notice', 'নোটিশ', 'announcement', 'ঘোষণা', 'exam', 'পরীক্ষা', 
                      'deadline', 'শেষ তারিখ', 'form', 'ফর্ম'],
            'faculty': ['teacher', 'শিক্ষক', 'faculty', 'professor', 'প্রফেসর', 
                       'department', 'বিভাগ', 'sir', 'madam'],
            'library': ['library', 'লাইব্রেরি', 'book', 'বই', 'timing', 'সময়'],
            'general': []
        }
        logger.info("QueryRouter initialized")
    
    def route_query(self, user_query: str, language: str = 'bn') -> Dict:
        """
        Main routing function following complete workflow
        
        Args:
            user_query: User's question
            language: 'bn' or 'en'
            
        Returns:
            Response dict with answer and metadata
        """
        try:
            logger.info(f"Processing query: {user_query}")
            
            # Step 1: Select Agent
            agent_type = self._select_agent(user_query)
            logger.info(f"Selected agent: {agent_type}")
            
            # Step 2: Check FAISS cache first (if available)
            cached_results = []
            if self.faiss_store:
                try:
                    cached_results = self.faiss_store.search(
                        user_query, 
                        top_k=Config.TOP_K_RESULTS,
                        threshold=Config.SIMILARITY_THRESHOLD
                    )
                except Exception as e:
                    logger.warning(f"FAISS search failed: {str(e)}")
                    cached_results = []
            
            # If good cached results exist, use them
            if cached_results and cached_results[0].get('score', 0) > 0.8:
                logger.info("Using cached results (high similarity)")
                context = self._format_context(cached_results)
                answer = self._generate_answer(user_query, context, language)
                
                return {
                    'success': True,
                    'answer': answer,
                    'agent': agent_type,
                    'source': 'cache',
                    'results': cached_results
                }
            
            # Step 3: Search Google (if cache miss or low similarity)
            logger.info("Cache miss or low similarity, searching web...")
            search_results = self._search_web(user_query, agent_type)
            
            if not search_results:
                logger.warning("No search results found, trying to generate answer from LLM knowledge")
                # Try to generate a helpful response even without search results
                try:
                    fallback_context = f"User asked about: {user_query}. This is related to {agent_type} information at {Config.UNIVERSITY_NAME}."
                    answer = self._generate_answer(user_query, fallback_context, language)
                    return {
                        'success': True,
                        'answer': answer,
                        'agent': agent_type,
                        'source': 'llm_fallback',
                        'results': []
                    }
                except Exception as e:
                    logger.error(f"Fallback answer generation failed: {str(e)}")
                    return {
                        'success': False,
                        'answer': self._get_no_results_message(language),
                        'agent': agent_type,
                        'source': 'none',
                        'results': []
                    }
            
            # Step 4: Filter URLs (official only)
            logger.info(f"Filtering {len(search_results)} search results...")
            filtered_results = self.url_filter.filter_search_results(search_results)
            
            if not filtered_results:
                return {
                    'success': False,
                    'answer': self._get_no_official_urls_message(language),
                    'agent': agent_type,
                    'source': 'filtered_out',
                    'results': []
                }
            
            # Step 5: Scrape & Clean content (with timeout per URL)
            logger.info(f"Scraping {len(filtered_results)} URLs...")
            scraped_docs = []
            import time as time_module
            scrape_start_time = time_module.time()
            max_scrape_time = 120  # Max 30 seconds total for scraping
            
            for result in filtered_results[:5]:  # Limit to top 5
                # Check if we've exceeded total scraping time
                if time_module.time() - scrape_start_time > max_scrape_time:
                    logger.warning(f"Scraping timeout ({max_scrape_time}s), using {len(scraped_docs)} available results")
                    break
                
                try:
                    start_scrape = time_module.time()
                    doc = self.scraper.scrape_url(result['url'])
                    scrape_time = time_module.time() - start_scrape
                    if doc and doc.get('content'):
                        scraped_docs.append(doc)
                        logger.info(f"Scraped {result['url']} in {scrape_time:.2f}s")
                except Exception as e:
                    logger.warning(f"Failed to scrape {result['url']}: {str(e)}")
                    continue
            
            if not scraped_docs:
                return {
                    'success': False,
                    'answer': self._get_scraping_error_message(language),
                    'agent': agent_type,
                    'source': 'scraping_failed',
                    'results': []
                }
            
            # Step 6: Store in FAISS (if available)
            if self.faiss_store:
                try:
                    logger.info(f"Storing {len(scraped_docs)} documents in FAISS...")
                    self.faiss_store.add_documents(scraped_docs)
                except Exception as e:
                    logger.warning(f"Failed to store in FAISS: {str(e)}")
            
            # Step 7: Semantic Search in newly added content (if FAISS available)
            fresh_results = []
            if self.faiss_store:
                try:
                    fresh_results = self.faiss_store.search(
                        user_query,
                        top_k=Config.TOP_K_RESULTS,
                        threshold=Config.SIMILARITY_THRESHOLD
                    )
                except Exception as e:
                    logger.warning(f"FAISS search failed: {str(e)}")
                    # Fallback to using scraped content directly
                    fresh_results = [{'title': doc.get('title', ''), 'url': doc.get('url', ''), 
                                    'preview': doc.get('content', '')[:200]} for doc in scraped_docs[:3]]
            
            # Step 8: Generate Answer with LLM
            context = self._format_context(fresh_results)
            answer = self._generate_answer(user_query, context, language)
            
            return {
                'success': True,
                'answer': answer,
                'agent': agent_type,
                'source': 'fresh',
                'results': fresh_results
            }
            
        except Exception as e:
            logger.error(f"Error in route_query: {str(e)}", exc_info=True)
            return {
                'success': False,
                'answer': self._get_error_message(language),
                'agent': 'error',
                'source': 'error',
                'error': str(e)
            }
    
    def _select_agent(self, query: str) -> str:
        """Classify query to select appropriate agent"""
        query_lower = query.lower()
        
        for agent_type, keywords in self.agent_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return agent_type
        
        return 'general'
    
    def _search_web(self, query: str, agent_type: str) -> List[Dict]:
        """Search web based on agent type"""
        try:
            # Enhance query with university context
            enhanced_query = f"{Config.UNIVERSITY_NAME} {query}"
            
            # Add agent-specific keywords
            if agent_type == 'notice':
                enhanced_query += " notice announcement"
            elif agent_type == 'faculty':
                enhanced_query += " faculty teacher professor"
            elif agent_type == 'library':
                enhanced_query += " library"
            
            logger.info(f"Searching with query: {enhanced_query}")
            logger.info(f"University domain: {Config.UNIVERSITY_DOMAIN}")
            
            # Search university website
            results = self.search_api.search_university(
                enhanced_query,
                num_results=Config.MAX_SEARCH_RESULTS
            )
            
            logger.info(f"Search returned {len(results)} results")
            
            # If no results with site restriction, try without restriction
            if not results and Config.UNIVERSITY_DOMAIN:
                logger.warning("No results with site restriction, trying broader search...")
                results = self.search_api.search(
                    enhanced_query,
                    num_results=Config.MAX_SEARCH_RESULTS,
                    site_restrict=None  # No site restriction
                )
                logger.info(f"Broader search returned {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in _search_web: {str(e)}", exc_info=True)
            return []
    
    def _format_context(self, results: List[Dict]) -> str:
        """Format search results as context for LLM"""
        if not results:
            return "No relevant information found."
        
        context_parts = []
        for idx, result in enumerate(results, 1):
            context_parts.append(
                f"[Source {idx}]\n"
                f"Title: {result.get('title', 'N/A')}\n"
                f"URL: {result.get('url', 'N/A')}\n"
                f"Content: {result.get('preview', '')}\n"
            )
        
        return "\n\n".join(context_parts)
    
    def _generate_answer(self, query: str, context: str, language: str) -> str:
        """Generate answer using LLM"""
        try:
            # Create prompt based on language
            if language == 'bn':
                prompt_template = """তুমি একজন বিশ্ববিদ্যালয়ের সহায়ক AI। নিচের তথ্যের উপর ভিত্তি করে প্রশ্নের উত্তর দাও।

প্রশ্ন: {query}

তথ্য:
{context}

নির্দেশনা:
- সংক্ষিপ্ত এবং সঠিক উত্তর দিতে হবে
- উত্তর বাংলায় লিখতে হবে
- তারিখ, সময় ইত্যাদি গুরুত্বপূর্ণ তথ্য অবশ্যই উল্লেখ করতে হবে
- উৎস থেকে প্রাপ্ত তথ্য ব্যবহার করতে হবে

উত্তর:"""
            else:
                prompt_template = """You are a helpful university assistant. Answer the question based on the information provided below.

Question: {query}

Information:
{context}

Instructions:
- Provide a concise and accurate answer
- Include important details like dates, times, deadlines
- Use the information from the sources provided

Answer:"""
            
            # Format prompt directly without PromptTemplate
            formatted_prompt = prompt_template.format(query=query, context=context)
            
            # Generate response
            response = self.llm.invoke(formatted_prompt)
            
            if hasattr(response, 'content'):
                return response.content.strip()
            return str(response).strip()
            
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            return self._get_error_message(language)
    
    def _get_no_results_message(self, language: str) -> str:
        """Message when no search results found"""
        if language == 'bn':
            return "দুঃখিত, আপনার প্রশ্নের উত্তর খুঁজে পাওয়া যায়নি। অনুগ্রহ করে আরও নির্দিষ্ট প্রশ্ন করুন।"
        return "Sorry, I couldn't find any results for your question. Please try asking more specifically."
    
    def _get_no_official_urls_message(self, language: str) -> str:
        """Message when no official URLs found"""
        if language == 'bn':
            return "দুঃখিত, কোনো অফিসিয়াল বিশ্ববিদ্যালয় তথ্য খুঁজে পাওয়া যায়নি।"
        return "Sorry, no official university information was found."
    
    def _get_scraping_error_message(self, language: str) -> str:
        """Message when scraping fails"""
        if language == 'bn':
            return "দুঃখিত, ওয়েবসাইট থেকে তথ্য সংগ্রহ করতে সমস্যা হয়েছে। পরে আবার চেষ্টা করুন।"
        return "Sorry, there was an error retrieving information from the website. Please try again later."
    
    def _get_error_message(self, language: str) -> str:
        """Generic error message"""
        if language == 'bn':
            return "দুঃখিত, একটি ত্রুটি ঘটেছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।"
        return "Sorry, an error occurred. Please try again later."
