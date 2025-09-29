"""
Configuration settings for the agent service
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Redis configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    serpapi_key: Optional[str] = os.getenv("SERPAPI_KEY")
    alpha_vantage_api_key: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    fmp_api_key: Optional[str] = os.getenv("FMP_API_KEY")
    
    # Vector database
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    pinecone_environment: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "finance-research-memory")
    use_pgvector: bool = os.getenv("USE_PGVECTOR", "false").lower() == "true"
    
    # LLM configuration
    default_llm: str = os.getenv("DEFAULT_LLM", "openai")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    # Agent configuration
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    max_sources_per_response: int = int(os.getenv("MAX_SOURCES_PER_RESPONSE", "8"))
    research_depth: str = os.getenv("RESEARCH_DEPTH", "deep")  # shallow, medium, deep
    
    # Timeout settings (seconds)
    agent_timeout: int = int(os.getenv("AGENT_TIMEOUT", "300"))
    search_timeout: int = int(os.getenv("SEARCH_TIMEOUT", "30"))
    scraping_timeout: int = int(os.getenv("SCRAPING_TIMEOUT", "15"))
    
    # Memory settings
    memory_checkpoint_ttl: int = int(os.getenv("MEMORY_CHECKPOINT_TTL", "86400"))  # 24 hours
    memory_similarity_threshold: float = float(os.getenv("MEMORY_SIMILARITY_THRESHOLD", "0.7"))
    memory_max_tokens: int = int(os.getenv("MEMORY_MAX_TOKENS", "2000"))
    
    # CORS settings
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "info").upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()