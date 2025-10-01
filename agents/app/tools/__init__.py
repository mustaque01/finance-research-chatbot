"""
Tools package initialization
"""

# This allows importing tools from the package
from .web_search import WebSearchTool
from .web_scraper import WebScraperTool

__all__ = ['WebSearchTool', 'WebScraperTool']