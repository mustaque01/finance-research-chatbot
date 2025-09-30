"""
Memory Manager - Orchestrates short-term and long-term memory operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .short_term import ShortTermMemory, get_short_term_memory
from .long_term import LongTermMemory, get_long_term_memory
from app.core.logging import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """
    Unified memory management interface
    Orchestrates operations between short-term and long-term memory
    """
    
    def __init__(self):
        self.short_term: Optional[ShortTermMemory] = None
        self.long_term: Optional[LongTermMemory] = None
        
    async def initialize(self):
        """Initialize both memory systems"""
        try:
            self.short_term = await get_short_term_memory()
            self.long_term = await get_long_term_memory()
            logger.info("✅ Memory manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            raise
    
    # Conversation Memory
    
    async def store_conversation_exchange(
        self,
        thread_id: str,
        user_id: str,
        query: str,
        response: str,
        sources: List[Dict[str, Any]] = None,
        analysis: Dict[str, Any] = None,
        insights: List[Dict[str, Any]] = None
    ) -> bool:
        """Store a complete conversation exchange in both memory systems"""
        
        try:
            # Store in short-term memory for quick access
            short_term_success = False
            if self.short_term:
                short_term_success = await self.short_term.store_conversation(
                    thread_id=thread_id,
                    user_id=user_id,
                    query=query,
                    response=response,
                    sources=sources,
                    analysis=analysis
                )
            
            # Extract and store insights in long-term memory
            long_term_success = False
            if self.long_term and insights:
                stored_count = await self.long_term.store_insights(
                    user_id=user_id,
                    thread_id=thread_id,
                    insights=insights
                )
                long_term_success = stored_count > 0
            
            logger.debug("Conversation exchange stored",
                        thread_id=thread_id,
                        short_term=short_term_success,
                        long_term=long_term_success)
            
            return short_term_success or long_term_success
            
        except Exception as e:
            logger.error(f"Failed to store conversation exchange: {e}")
            return False
    
    async def get_conversation_context(
        self,
        thread_id: str,
        user_id: str,
        include_history: bool = True,
        include_insights: bool = True,
        max_history: int = 10
    ) -> Dict[str, Any]:
        """Get comprehensive conversation context"""
        
        context = {
            "thread_id": thread_id,
            "user_id": user_id,
            "conversation_history": [],
            "relevant_insights": [],
            "context_summary": {}
        }
        
        try:
            # Get recent conversation history from short-term memory
            if include_history and self.short_term:
                history = await self.short_term.get_conversation_history(
                    thread_id=thread_id,
                    limit=max_history
                )
                context["conversation_history"] = history
            
            # Get relevant insights from long-term memory
            if include_insights and self.long_term and context["conversation_history"]:
                # Use recent queries to find relevant insights
                recent_queries = [
                    conv.get("query", "") 
                    for conv in context["conversation_history"][-3:]  # Last 3 exchanges
                ]
                query_text = " ".join(recent_queries)
                
                if query_text.strip():
                    insights = await self.long_term.search_memories(
                        user_id=user_id,
                        query=query_text,
                        limit=5,
                        min_confidence=0.7
                    )
                    context["relevant_insights"] = insights
            
            # Create context summary
            context["context_summary"] = {
                "history_length": len(context["conversation_history"]),
                "insights_found": len(context["relevant_insights"]),
                "last_interaction": (
                    context["conversation_history"][0].get("timestamp")
                    if context["conversation_history"] else None
                )
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return context
    
    # Research Memory
    
    async def store_research_session(
        self,
        session_id: str,
        user_id: str,
        query: str,
        research_results: Dict[str, Any],
        key_insights: List[Dict[str, Any]] = None
    ) -> bool:
        """Store research session results"""
        
        try:
            success_count = 0
            
            # Cache research results in short-term memory
            if self.short_term:
                query_hash = str(hash(f"{user_id}:{query}"))
                cached = await self.short_term.cache_research_results(
                    query_hash=query_hash,
                    results=research_results,
                    ttl=3600  # 1 hour
                )
                if cached:
                    success_count += 1
            
            # Store insights in long-term memory
            if self.long_term and key_insights:
                stored = await self.long_term.store_insights(
                    user_id=user_id,
                    thread_id=session_id,
                    insights=key_insights
                )
                if stored > 0:
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to store research session: {e}")
            return False
    
    async def get_cached_research(
        self,
        user_id: str, 
        query: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached research results if available"""
        
        try:
            if not self.short_term:
                return None
            
            query_hash = str(hash(f"{user_id}:{query}"))
            return await self.short_term.get_cached_research(query_hash)
            
        except Exception as e:
            logger.error(f"Failed to get cached research: {e}")
            return None
    
    # User Knowledge Profile
    
    async def build_user_knowledge_profile(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Build a knowledge profile for the user based on their memory"""
        
        profile = {
            "user_id": user_id,
            "interests": [],
            "expertise_areas": [],
            "frequent_queries": [],
            "key_insights": [],
            "interaction_patterns": {},
            "generated_at": datetime.now().isoformat()
        }
        
        try:
            # Get user insights from long-term memory
            if self.long_term:
                insights = await self.long_term.get_user_insights(
                    user_id=user_id,
                    limit=100
                )
                
                # Analyze insights to extract interests and expertise
                entity_counts = {}
                insight_types = {}
                
                for insight in insights:
                    # Count entities (companies, topics, etc.)
                    for entity in insight.get("entities", []):
                        entity_counts[entity] = entity_counts.get(entity, 0) + 1
                    
                    # Count insight types
                    insight_type = insight.get("type", "general")
                    insight_types[insight_type] = insight_types.get(insight_type, 0) + 1
                
                # Top interests (most mentioned entities)
                profile["interests"] = [
                    {"entity": entity, "mentions": count}
                    for entity, count in sorted(entity_counts.items(), 
                                              key=lambda x: x[1], reverse=True)[:10]
                ]
                
                # Expertise areas (insight types)
                profile["expertise_areas"] = [
                    {"area": area, "insights": count}
                    for area, count in sorted(insight_types.items(),
                                            key=lambda x: x[1], reverse=True)[:5]
                ]
                
                # Recent key insights
                profile["key_insights"] = insights[:10]  # Most recent 10
            
            # Get interaction patterns from short-term memory
            if self.short_term:
                memory_stats = await self.short_term.get_memory_stats()
                if memory_stats.get("status") == "available":
                    profile["interaction_patterns"] = {
                        "recent_activity": True,
                        "memory_usage": memory_stats.get("key_counts", {})
                    }
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to build user knowledge profile: {e}")
            return profile
    
    # Memory Maintenance
    
    async def get_memory_health_status(self) -> Dict[str, Any]:
        """Get overall memory system health status"""
        
        status = {
            "overall_status": "unknown",
            "short_term_memory": {},
            "long_term_memory": {},
            "recommendations": [],
            "checked_at": datetime.now().isoformat()
        }
        
        try:
            # Check short-term memory
            if self.short_term:
                st_stats = await self.short_term.get_memory_stats()
                status["short_term_memory"] = st_stats
            
            # Check long-term memory
            if self.long_term:
                lt_stats = await self.long_term.get_memory_stats()
                status["long_term_memory"] = lt_stats
            
            # Determine overall status
            st_healthy = status["short_term_memory"].get("status") == "available"
            lt_healthy = status["long_term_memory"].get("vector_db_type") is not None
            
            if st_healthy and lt_healthy:
                status["overall_status"] = "healthy"
            elif st_healthy or lt_healthy:
                status["overall_status"] = "partial"
                status["recommendations"].append("Some memory systems are unavailable")
            else:
                status["overall_status"] = "degraded"
                status["recommendations"].append("Memory systems need attention")
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get memory health status: {e}")
            status["overall_status"] = "error"
            status["error"] = str(e)
            return status
    
    async def perform_memory_maintenance(
        self,
        cleanup_expired: bool = True,
        cleanup_old_insights: bool = False,
        days_old: int = 90
    ) -> Dict[str, Any]:
        """Perform memory system maintenance"""
        
        maintenance_results = {
            "started_at": datetime.now().isoformat(),
            "short_term_cleanup": {},
            "long_term_cleanup": {},
            "errors": []
        }
        
        try:
            # Short-term memory cleanup
            if cleanup_expired and self.short_term:
                st_results = await self.short_term.cleanup_expired_keys()
                maintenance_results["short_term_cleanup"] = st_results
            
            # Long-term memory cleanup (if requested)
            if cleanup_old_insights and self.long_term:
                # This would need user-specific cleanup calls
                # Left as placeholder for batch operations
                maintenance_results["long_term_cleanup"] = {
                    "note": "Long-term cleanup requires user-specific operations"
                }
            
            maintenance_results["completed_at"] = datetime.now().isoformat()
            
            return maintenance_results
            
        except Exception as e:
            logger.error(f"Memory maintenance failed: {e}")
            maintenance_results["errors"].append(str(e))
            return maintenance_results


# Global instance
_memory_manager: Optional[MemoryManager] = None

async def get_memory_manager() -> MemoryManager:
    """Get or create memory manager instance"""
    global _memory_manager
    
    if _memory_manager is None:
        _memory_manager = MemoryManager()
        await _memory_manager.initialize()
    
    return _memory_manager