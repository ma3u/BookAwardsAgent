"""
Web search module for the Book Awards Websearch Agent.
Handles searching for book awards and extracting initial URLs.
"""

import time
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any

from .config import SEARCH_QUERIES, USER_AGENT, MAX_SEARCH_RESULTS, REQUEST_DELAY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebSearcher:
    """Class to handle web searching for book awards."""
    
    def __init__(self):
        """Initialize the WebSearcher with default headers."""
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def search_for_book_awards(self) -> List[Dict[str, str]]:
        """
        Search for book awards using predefined queries.
        
        Returns:
            List of dictionaries containing award information with URLs
        """
        all_results = []
        
        for query in SEARCH_QUERIES:
            logger.info(f"Searching for: {query}")
            results = self._perform_search(query)
            all_results.extend(results)
            time.sleep(max(REQUEST_DELAY, 5))  # Increased delay to avoid rate limiting
            
        # Remove duplicates based on URL
        unique_results = self._remove_duplicates(all_results)
        logger.info(f"Found {len(unique_results)} unique book award websites")
        
        return unique_results
    
    def _perform_search(self, query: str) -> List[Dict[str, str]]:
        """
        Perform a search using the given query with DuckDuckGo API, with retry/backoff on rate limit.
        Args:
            query: Search query string
        Returns:
            List of dictionaries with search results
        """
        from duckduckgo_search import DDGS
        from duckduckgo_search.exceptions import DuckDuckGoSearchException
        max_attempts = 4
        base_delay = 5
        for attempt in range(max_attempts):
            try:
                logger.debug(f"Searching DuckDuckGo for: {query} (attempt {attempt + 1})")
                with DDGS() as ddgs:
                    results = []
                    for result in ddgs.text(query, max_results=MAX_SEARCH_RESULTS):
                        title = result.get('title', '')
                        url = result.get('href', '')
                        snippet = result.get('body', '')
                        if self._is_likely_book_award(title, snippet):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet
                            })
                            logger.debug(f"Added result: {title} - {url}")
                    logger.info(f"Found {len(results)} valid results for query: {query}")
                    return results
            except DuckDuckGoSearchException as e:
                logger.warning(f"DuckDuckGo rate limit or error: {e}. Retrying after backoff.")
                time.sleep(base_delay * (2 ** attempt))
            except Exception as e:
                logger.error(f"Error performing search for query '{query}': {e}", exc_info=True)
                break
        logger.error(f"Failed to retrieve results for query '{query}' after {max_attempts} attempts.")
        return []

        """
        Perform a search using the given query with DuckDuckGo API.
        
        Args:
            query: Search query string
            
        Returns:
            List of dictionaries with search results
        """
        from duckduckgo_search import DDGS
        
        try:
            logger.debug(f"Searching DuckDuckGo for: {query}")
            
            # Initialize DuckDuckGo search
            with DDGS() as ddgs:
                # Get search results
                results = []
                for result in ddgs.text(query, max_results=MAX_SEARCH_RESULTS):
                    title = result.get('title', '')
                    url = result.get('href', '')
                    snippet = result.get('body', '')
                    
                    # Only include results that are likely to be book awards
                    if self._is_likely_book_award(title, snippet):
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                        logger.debug(f"Added result: {title} - {url}")
                
                logger.info(f"Found {len(results)} valid results for query: {query}")
                return results
                
        except Exception as e:
            logger.error(f"Error performing search for query '{query}': {e}", exc_info=True)
            return []
    
    def _is_likely_book_award(self, title: str, snippet: str) -> bool:
        """
        Determine if a search result is likely to be a book award.
        
        Args:
            title: Title of the search result
            snippet: Snippet text from the search result
            
        Returns:
            Boolean indicating if the result is likely a book award
        """
        # Keywords that suggest a book award
        award_keywords = [
            'book award', 'literary prize', 'book prize', 'writing award',
            'author award', 'publishing award', 'book contest'
        ]
        
        # Check if any keywords are in the title or snippet
        text = (title + ' ' + snippet).lower()
        return any(keyword in text for keyword in award_keywords)
    
    def _remove_duplicates(self, results: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Remove duplicate results based on URL.
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Deduplicated list of results
        """
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result['url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
                
        return unique_results
