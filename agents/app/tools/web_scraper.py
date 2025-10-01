"""
Web Scraper Tool - Handles web content scraping for research
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
import json
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class WebScraperTool:
    """Tool for scraping web content from URLs"""
    
    def __init__(self):
        self.session = None
        self.max_content_length = 10000  # Maximum content length to extract
        self.timeout = 30  # Request timeout in seconds
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def scrape(
        self, 
        url: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scrape content from a URL
        
        Args:
            url: URL to scrape
            metadata: Additional metadata about the URL
            
        Returns:
            Dictionary with scraped content and metadata
        """
        
        logger.info("Starting web scraping", url=url[:100])
        
        if not url:
            return self._create_error_result("Empty URL provided")
        
        if not self.session:
            async with self:
                return await self._perform_scrape(url, metadata)
        else:
            return await self._perform_scrape(url, metadata)
    
    async def _perform_scrape(
        self, 
        url: str, 
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Internal method to perform the actual scraping"""
        
        try:
            # Validate URL
            if not self._is_valid_url(url):
                return self._create_error_result(f"Invalid URL: {url}")
            
            # Check if URL is accessible
            if not await self._is_url_accessible(url):
                return self._create_error_result(f"URL not accessible: {url}")
            
            # Fetch content
            content_data = await self._fetch_content(url)
            
            if not content_data:
                return self._create_error_result(f"No content retrieved from: {url}")
            
            # Parse and extract relevant content
            parsed_content = await self._parse_content(content_data, url)
            
            # Create result
            result = {
                'url': url,
                'title': parsed_content.get('title', ''),
                'content': parsed_content.get('content', ''),
                'snippet': parsed_content.get('snippet', ''),
                'domain': self._extract_domain(url),
                'content_type': parsed_content.get('content_type', 'text/html'),
                'content_length': len(parsed_content.get('content', '')),
                'scraped_at': datetime.now().isoformat(),
                'success': True,
                'error': None
            }
            
            # Add metadata if provided
            if metadata:
                result.update({
                    'search_title': metadata.get('title', ''),
                    'search_snippet': metadata.get('snippet', ''),
                    'search_rank': metadata.get('rank', 0)
                })
            
            logger.info("Web scraping completed",
                       url=url[:50],
                       content_length=len(parsed_content.get('content', '')),
                       title_length=len(parsed_content.get('title', '')))
            
            return result
            
        except Exception as e:
            logger.error("Web scraping failed", url=url[:50], error=str(e))
            return self._create_error_result(f"Scraping error: {str(e)}")
    
    async def _fetch_content(self, url: str) -> Optional[str]:
        """Fetch raw content from URL"""
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Only process text content
                    if 'text/html' in content_type or 'text/plain' in content_type:
                        content = await response.text()
                        return content
                    else:
                        logger.warning("Unsupported content type", 
                                     url=url[:50], 
                                     content_type=content_type)
                        return None
                else:
                    logger.warning("HTTP error", 
                                 url=url[:50], 
                                 status=response.status)
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning("Request timeout", url=url[:50])
            return None
        except Exception as e:
            logger.warning("Request failed", url=url[:50], error=str(e))
            return None
    
    async def _parse_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse HTML content and extract relevant information"""
        
        try:
            # Try to use BeautifulSoup if available, otherwise use regex
            try:
                from bs4 import BeautifulSoup
                return await self._parse_with_bs4(html_content)
            except ImportError:
                logger.info("BeautifulSoup not available, using regex parsing")
                return await self._parse_with_regex(html_content)
                
        except Exception as e:
            logger.warning("Content parsing failed", error=str(e))
            return {
                'title': '',
                'content': html_content[:self.max_content_length],
                'snippet': html_content[:200],
                'content_type': 'text/html'
            }
    
    async def _parse_with_bs4(self, html_content: str) -> Dict[str, Any]:
        """Parse content using BeautifulSoup"""
        
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ''
        
        # Extract main content - try different selectors
        content_selectors = [
            'main', 'article', '.content', '#content', 
            '.main-content', '.article-content', '.post-content',
            'div[role="main"]', '.entry-content'
        ]
        
        main_content = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                main_content = content_element.get_text(separator=' ', strip=True)
                break
        
        # If no main content found, use body
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator=' ', strip=True)
        
        # Clean and limit content
        content = self._clean_text(main_content)[:self.max_content_length]
        
        # Create snippet
        snippet = content[:300] + "..." if len(content) > 300 else content
        
        return {
            'title': title,
            'content': content,
            'snippet': snippet,
            'content_type': 'text/html'
        }
    
    async def _parse_with_regex(self, html_content: str) -> Dict[str, Any]:
        """Parse content using regex (fallback method)"""
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ''
        
        # Remove script and style tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Clean text
        content = self._clean_text(content)[:self.max_content_length]
        
        # Create snippet
        snippet = content[:300] + "..." if len(content) > 300 else content
        
        return {
            'title': self._clean_text(title),
            'content': content,
            'snippet': snippet,
            'content_type': 'text/html'
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        
        if not text:
            return ""
        
        # Replace multiple whitespaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Remove HTML entities
        html_entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
            '&#39;': "'", '&nbsp;': ' ', '&copy;': '©', '&reg;': '®'
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        return text.strip()
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    async def _is_url_accessible(self, url: str) -> bool:
        """Check if URL is accessible (basic check)"""
        
        # Check against blocklist
        blocked_domains = [
            'facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com',
            'reddit.com', 'pinterest.com', 'linkedin.com'  # Social media - often require auth
        ]
        
        domain = self._extract_domain(url)
        if any(blocked in domain.lower() for blocked in blocked_domains):
            logger.info("Skipping blocked domain", domain=domain)
            return False
        
        # Check for obvious non-content URLs
        if any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']):
            logger.info("Skipping document URL", url=url[:50])
            return False
        
        return True
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return ""
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result dictionary"""
        
        return {
            'url': '',
            'title': '',
            'content': '',
            'snippet': '',
            'domain': '',
            'content_type': '',
            'content_length': 0,
            'scraped_at': datetime.now().isoformat(),
            'success': False,
            'error': error_message
        }
    
    async def scrape_multiple(
        self, 
        urls: List[str], 
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently"""
        
        logger.info("Starting concurrent scraping", urls_count=len(urls))
        
        # Limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape(url)
        
        # Create tasks
        tasks = [scrape_with_semaphore(url) for url in urls]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Scraping failed for URL", 
                           url=urls[i][:50], 
                           error=str(result))
                processed_results.append(self._create_error_result(f"Exception: {str(result)}"))
            else:
                processed_results.append(result)
        
        successful_scrapes = sum(1 for r in processed_results if r.get('success', False))
        logger.info("Concurrent scraping completed",
                   total_urls=len(urls),
                   successful=successful_scrapes,
                   failed=len(urls) - successful_scrapes)
        
        return processed_results