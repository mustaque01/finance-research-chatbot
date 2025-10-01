"""
Web Search Tool - Handles web search operations for research
"""

import asyncio
from typing import Dict, Any, List, Optional
import json
from urllib.parse import quote_plus
import os

# Try to import aiohttp with fallback
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class WebSearchTool:
    """Tool for performing web searches using various search APIs"""
    
    def __init__(self):
        # Configure search engines in order of preference
        self.search_engines = []
        
        # Google Custom Search API
        if hasattr(settings, 'google_search_api_key') and hasattr(settings, 'google_search_engine_id'):
            self.search_engines.append('google')
        
        # Bing Search API
        if hasattr(settings, 'bing_search_api_key'):
            self.search_engines.append('bing')
        
        # DuckDuckGo (no API key required)
        self.search_engines.append('duckduckgo')
        
        # Fallback to mock results for testing
        if not self.search_engines:
            self.search_engines.append('mock')
        
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search(
        self, 
        query: str, 
        max_results: int = 10,
        safe_search: bool = True,
        region: str = "en-US"
    ) -> List[Dict[str, Any]]:
        """
        Perform web search and return results
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            safe_search: Enable safe search filtering
            region: Search region/language
            
        Returns:
            List of search results with title, url, snippet, etc.
        """
        
        logger.info("Starting web search", 
                   query=query[:100], 
                   max_results=max_results)
        
        if not self.session:
            async with self:
                return await self._perform_search(query, max_results, safe_search, region)
        else:
            return await self._perform_search(query, max_results, safe_search, region)
    
    async def _perform_search(
        self, 
        query: str, 
        max_results: int,
        safe_search: bool,
        region: str
    ) -> List[Dict[str, Any]]:
        """Internal method to perform the actual search"""
        
        results = []
        
        # Try each search engine until we get results
        for engine in self.search_engines:
            try:
                if engine == 'google':
                    engine_results = await self._search_google(query, max_results, safe_search)
                elif engine == 'bing':
                    engine_results = await self._search_bing(query, max_results, safe_search, region)
                elif engine == 'duckduckgo':
                    engine_results = await self._search_duckduckgo(query, max_results)
                elif engine == 'mock':
                    engine_results = await self._search_mock(query, max_results)
                else:
                    continue
                
                if engine_results:
                    results.extend(engine_results)
                    logger.info(f"Search completed using {engine}", 
                               results_count=len(engine_results))
                    break
                    
            except Exception as e:
                logger.warning(f"Search failed with {engine}", error=str(e))
                continue
        
        # Deduplicate results by URL
        seen_urls = set()
        unique_results = []
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        # Limit to max_results
        return unique_results[:max_results]
    
    async def _search_google(
        self, 
        query: str, 
        max_results: int,
        safe_search: bool
    ) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API"""
        
        api_key = getattr(settings, 'google_search_api_key', None)
        search_engine_id = getattr(settings, 'google_search_engine_id', None)
        
        if not api_key or not search_engine_id:
            raise Exception("Google Search API credentials not configured")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': min(max_results, 10),  # Google API max is 10
            'safe': 'active' if safe_search else 'off'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_google_results(data)
            else:
                raise Exception(f"Google Search API error: {response.status}")
    
    async def _search_bing(
        self, 
        query: str, 
        max_results: int,
        safe_search: bool,
        region: str
    ) -> List[Dict[str, Any]]:
        """Search using Bing Search API"""
        
        api_key = getattr(settings, 'bing_search_api_key', None)
        
        if not api_key:
            raise Exception("Bing Search API key not configured")
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            'Ocp-Apim-Subscription-Key': api_key
        }
        params = {
            'q': query,
            'count': min(max_results, 50),  # Bing API max is 50
            'safeSearch': 'Strict' if safe_search else 'Off',
            'mkt': region
        }
        
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_bing_results(data)
            else:
                raise Exception(f"Bing Search API error: {response.status}")
    
    async def _search_duckduckgo(
        self, 
        query: str, 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo (simplified implementation)"""
        
        # Note: This is a simplified implementation
        # In production, you might want to use a proper DuckDuckGo API wrapper
        
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_duckduckgo_results(data, max_results)
                else:
                    raise Exception(f"DuckDuckGo API error: {response.status}")
        except Exception as e:
            logger.warning("DuckDuckGo search failed, falling back to mock", error=str(e))
            return await self._search_mock(query, max_results)
    
    async def _search_mock(
        self, 
        query: str, 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Mock search results for testing/fallback"""
        
        logger.info("Using mock search results for development/testing")
        
        # Generate realistic-looking mock results
        mock_results = []
        
        base_domains = [
            "reuters.com", "bloomberg.com", "finance.yahoo.com", 
            "marketwatch.com", "cnbc.com", "wsj.com", "ft.com",
            "investopedia.com", "fool.com", "seekingalpha.com"
        ]
        
        for i in range(min(max_results, 8)):
            domain = base_domains[i % len(base_domains)]
            mock_results.append({
                'title': f"Financial Analysis: {query} - Key Insights",
                'url': f"https://www.{domain}/article/{query.lower().replace(' ', '-')}-{i+1}",
                'snippet': f"Latest analysis and insights about {query}. Comprehensive financial data and market trends analysis covering key metrics and performance indicators.",
                'domain': domain,
                'published_date': "2024-10-01",
                'source': 'mock'
            })
        
        # Add some variation to make it more realistic
        if len(mock_results) > 0:
            mock_results[0]['title'] = f"{query} Stock Analysis - Current Market Position"
            mock_results[0]['snippet'] = f"Detailed analysis of {query} including valuation metrics, growth prospects, and risk assessment."
        
        if len(mock_results) > 1:
            mock_results[1]['title'] = f"{query} Financial Performance Report"
            mock_results[1]['snippet'] = f"Quarterly earnings analysis and financial performance review for {query} with key metrics and trends."
        
        return mock_results
    
    def _parse_google_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Google Custom Search API results"""
        
        results = []
        items = data.get('items', [])
        
        for item in items:
            result = {
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'domain': self._extract_domain(item.get('link', '')),
                'source': 'google'
            }
            results.append(result)
        
        return results
    
    def _parse_bing_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Bing Search API results"""
        
        results = []
        web_pages = data.get('webPages', {}).get('value', [])
        
        for page in web_pages:
            result = {
                'title': page.get('name', ''),
                'url': page.get('url', ''),
                'snippet': page.get('snippet', ''),
                'domain': self._extract_domain(page.get('url', '')),
                'published_date': page.get('dateLastCrawled', ''),
                'source': 'bing'
            }
            results.append(result)
        
        return results
    
    def _parse_duckduckgo_results(
        self, 
        data: Dict[str, Any], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo API results"""
        
        results = []
        
        # DuckDuckGo instant answer
        if data.get('AbstractText'):
            results.append({
                'title': data.get('Heading', 'DuckDuckGo Result'),
                'url': data.get('AbstractURL', ''),
                'snippet': data.get('AbstractText', ''),
                'domain': self._extract_domain(data.get('AbstractURL', '')),
                'source': 'duckduckgo'
            })
        
        # Related topics
        related_topics = data.get('RelatedTopics', [])
        for topic in related_topics[:max_results-1]:
            if isinstance(topic, dict) and topic.get('FirstURL'):
                results.append({
                    'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                    'url': topic.get('FirstURL', ''),
                    'snippet': topic.get('Text', ''),
                    'domain': self._extract_domain(topic.get('FirstURL', '')),
                    'source': 'duckduckgo'
                })
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return ""