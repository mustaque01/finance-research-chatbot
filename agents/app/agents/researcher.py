"""
Researcher Agent - Handles web search and content collection
"""

import asyncio
from typing import Dict, Any, List
import aiohttp
from bs4 import BeautifulSoup

from app.tools.web_search import WebSearchTool
from app.tools.web_scraper import WebScraperTool
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ResearcherAgent:
    """Agent responsible for researching and collecting information"""
    
    def __init__(self):
        self.web_search = WebSearchTool()
        self.web_scraper = WebScraperTool()
    
    async def analyze_query(
        self, 
        query: str, 
        conversation_history: List[Any] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze the user query to understand intent and extract entities"""
        
        logger.info("Analyzing query", query_length=len(query))
        
        # Simple query analysis - could be enhanced with NLP models
        query_lower = query.lower()
        
        # Detect financial entities
        entities = []
        financial_keywords = [
            "bank", "stock", "share", "equity", "bond", "investment",
            "portfolio", "market", "trading", "analysis", "valuation",
            "earnings", "revenue", "profit", "loss", "dividend"
        ]
        
        # Extract potential company names (capitalized words)
        words = query.split()
        for word in words:
            if word.isupper() or (word.istitle() and len(word) > 2):
                entities.append({"type": "company", "value": word})
        
        # Detect intent
        intent = "general_inquiry"
        if any(word in query_lower for word in ["compare", "vs", "versus"]):
            intent = "comparison"
        elif any(word in query_lower for word in ["analyze", "analysis"]):
            intent = "analysis"
        elif any(word in query_lower for word in ["price", "valuation", "worth"]):
            intent = "valuation"
        elif any(word in query_lower for word in ["forecast", "predict", "future"]):
            intent = "prediction"
        
        # Determine complexity
        complexity = "medium"
        if len(query.split()) > 15 or "and" in query_lower:
            complexity = "high"
        elif len(query.split()) < 8:
            complexity = "low"
        
        return {
            "intent": intent,
            "entities": entities,
            "complexity": complexity,
            "financial_context": any(keyword in query_lower for keyword in financial_keywords),
            "query_type": "financial_research",
        }
    
    async def plan_research(
        self,
        query_analysis: Dict[str, Any],
        research_depth: str = "deep",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Plan the research strategy based on query analysis"""
        
        logger.info("Planning research strategy", 
                   intent=query_analysis.get("intent"),
                   depth=research_depth)
        
        entities = query_analysis.get("entities", [])
        intent = query_analysis.get("intent", "general_inquiry")
        
        # Generate search queries
        search_queries = []
        base_query = metadata.get("original_query", "") if metadata else ""
        
        # Primary search query
        search_queries.append(base_query)
        
        # Entity-specific queries
        for entity in entities:
            if entity["type"] == "company":
                company = entity["value"]
                search_queries.extend([
                    f"{company} financial analysis",
                    f"{company} stock performance",
                    f"{company} quarterly results",
                ])
        
        # Intent-specific queries
        if intent == "comparison":
            search_queries.append(f"{base_query} peer comparison")
        elif intent == "valuation":
            search_queries.append(f"{base_query} valuation metrics")
        
        # Determine data sources needed
        data_sources = ["web_search"]
        if any(entity["type"] == "company" for entity in entities):
            data_sources.extend(["financial_data", "stock_data"])
        
        # Adjust strategy based on research depth
        if research_depth == "shallow":
            search_queries = search_queries[:3]
        elif research_depth == "deep":
            search_queries = search_queries[:8]
        else:  # medium
            search_queries = search_queries[:5]
        
        return {
            "strategy": f"{research_depth}_research",
            "search_queries": search_queries,
            "data_sources": data_sources,
            "priority_entities": entities[:3],  # Top 3 entities
            "estimated_time": self._estimate_research_time(len(search_queries)),
        }
    
    async def search_web(
        self,
        research_plan: Dict[str, Any],
        query_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute web searches based on the research plan"""
        
        search_queries = research_plan.get("search_queries", [])
        logger.info("Starting web search", queries_count=len(search_queries))
        
        all_results = []
        
        # Execute searches concurrently
        tasks = []
        for query in search_queries:
            task = self.web_search.search(
                query=query,
                max_results=settings.max_search_results // len(search_queries) or 2
            )
            tasks.append(task)
        
        # Wait for all searches to complete
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, results in enumerate(search_results):
            if isinstance(results, Exception):
                logger.error(f"Search failed for query {i}", error=str(results))
                continue
            
            if isinstance(results, list):
                all_results.extend(results)
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        logger.info("Web search completed", 
                   total_results=len(unique_results),
                   queries_executed=len(search_queries))
        
        return unique_results[:settings.max_search_results]
    
    async def scrape_content(
        self,
        search_results: List[Dict[str, Any]],
        query_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Scrape content from search results"""
        
        logger.info("Starting content scraping", urls_count=len(search_results))
        
        scraped_content = []
        
        # Scrape content concurrently
        tasks = []
        for result in search_results:
            task = self.web_scraper.scrape(
                url=result.get("url", ""),
                metadata=result
            )
            tasks.append(task)
        
        # Wait for all scraping to complete
        scraping_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, content in enumerate(scraping_results):
            if isinstance(content, Exception):
                logger.error(f"Scraping failed for URL {i}", error=str(content))
                continue
            
            if content and content.get("content"):
                scraped_content.append(content)
        
        logger.info("Content scraping completed", 
                   pages_scraped=len(scraped_content))
        
        return scraped_content
    
    async def deduplicate_sources(
        self,
        scraped_content: List[Dict[str, Any]],
        max_sources: int = 10
    ) -> List[Dict[str, Any]]:
        """Deduplicate and rank sources by relevance"""
        
        logger.info("Deduplicating sources", 
                   original_count=len(scraped_content),
                   max_sources=max_sources)
        
        if not scraped_content:
            return []
        
        # Simple deduplication by content similarity
        # In a real implementation, you'd use more sophisticated methods
        
        deduplicated = []
        seen_domains = {}
        
        # Sort by content length (longer content often more valuable)
        sorted_content = sorted(
            scraped_content,
            key=lambda x: len(x.get("content", "")),
            reverse=True
        )
        
        for content in sorted_content:
            domain = content.get("domain", "")
            content_length = len(content.get("content", ""))
            
            # Limit sources per domain
            if domain in seen_domains:
                if seen_domains[domain] >= 2:  # Max 2 sources per domain
                    continue
                seen_domains[domain] += 1
            else:
                seen_domains[domain] = 1
            
            # Only include sources with meaningful content
            if content_length > 100:  # Minimum content length
                deduplicated.append(content)
            
            # Stop when we reach max sources
            if len(deduplicated) >= max_sources:
                break
        
        logger.info("Source deduplication completed",
                   final_count=len(deduplicated))
        
        return deduplicated
    
    def _estimate_research_time(self, query_count: int) -> int:
        """Estimate research time in seconds"""
        base_time = 30  # Base time for setup
        per_query_time = 15  # Time per search query
        scraping_time = query_count * 5  # Time for scraping
        
        return base_time + (query_count * per_query_time) + scraping_time