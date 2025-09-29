"""
Agent capabilities endpoint
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from app.core.config import settings

router = APIRouter()


class CapabilityInfo(BaseModel):
    """Capability information model"""
    name: str
    description: str
    enabled: bool
    configuration: Dict[str, Any] = {}


class AgentCapabilities(BaseModel):
    """Agent capabilities response model"""
    version: str
    environment: str
    llm_providers: List[str]
    search_providers: List[str]
    data_sources: List[str]
    features: List[CapabilityInfo]


@router.get("/", response_model=AgentCapabilities)
async def get_capabilities() -> AgentCapabilities:
    """
    Get agent capabilities and configuration
    """
    # Determine available LLM providers
    llm_providers = []
    if settings.openai_api_key:
        llm_providers.append("openai")
    if settings.anthropic_api_key:
        llm_providers.append("anthropic")
    
    # Determine available search providers
    search_providers = []
    if settings.tavily_api_key:
        search_providers.append("tavily")
    if settings.serpapi_key:
        search_providers.append("serpapi")
    
    # Determine available data sources
    data_sources = ["yahoo_finance"]  # Always available
    if settings.alpha_vantage_api_key:
        data_sources.append("alpha_vantage")
    if settings.fmp_api_key:
        data_sources.append("financial_modeling_prep")
    
    # Define features
    features = [
        CapabilityInfo(
            name="web_research",
            description="Search and scrape web content for financial information",
            enabled=bool(search_providers),
            configuration={
                "max_results": settings.max_search_results,
                "timeout": settings.search_timeout,
            }
        ),
        CapabilityInfo(
            name="financial_data",
            description="Fetch real-time and historical financial data",
            enabled=bool(data_sources),
            configuration={
                "sources": data_sources,
            }
        ),
        CapabilityInfo(
            name="memory_system",
            description="Long-term and short-term memory for context retention",
            enabled=True,
            configuration={
                "short_term_ttl": settings.memory_checkpoint_ttl,
                "similarity_threshold": settings.memory_similarity_threshold,
                "use_vector_db": bool(settings.pinecone_api_key) or settings.use_pgvector,
            }
        ),
        CapabilityInfo(
            name="multi_agent_workflow",
            description="Coordinated multi-agent research and analysis",
            enabled=True,
            configuration={
                "research_depth": settings.research_depth,
                "max_sources": settings.max_sources_per_response,
            }
        ),
        CapabilityInfo(
            name="streaming_responses",
            description="Real-time streaming of responses and thinking process",
            enabled=True,
            configuration={
                "timeout": settings.agent_timeout,
            }
        ),
        CapabilityInfo(
            name="citation_tracking",
            description="Automatic source citation and deduplication",
            enabled=True,
            configuration={}
        ),
    ]
    
    return AgentCapabilities(
        version="1.0.0",
        environment=settings.environment,
        llm_providers=llm_providers,
        search_providers=search_providers,
        data_sources=data_sources,
        features=features,
    )