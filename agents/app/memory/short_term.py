"""
Short-term memory implementation using Redis
Handles conversation context, session state, and temporary caching
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ShortTermMemory:
    """
    Short-term memory for conversation context and temporary data storage
    Uses Redis for fast access and automatic expiration
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connection_pool = None
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self._connection_pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=True,
                retry_on_timeout=True,
                health_check_interval=30
            )
            self.redis_client = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Short-term memory (Redis) connected successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed, using fallback memory: {e}")
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.aclose()
        if self._connection_pool:
            await self._connection_pool.aclose()
    
    # Conversation Memory Methods
    
    async def store_conversation(
        self,
        thread_id: str,
        user_id: str,
        query: str,
        response: str,
        sources: List[Dict[str, Any]] = None,
        analysis: Dict[str, Any] = None,
        ttl: int = 3600  # 1 hour default
    ) -> bool:
        """Store conversation exchange in short-term memory"""
        
        conversation_data = {
            "thread_id": thread_id,
            "user_id": user_id,
            "query": query,
            "response": response,
            "sources": sources or [],
            "analysis": analysis or {},
            "timestamp": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
        }
        
        try:
            if self.redis_client:
                # Store individual conversation
                conv_key = f"conversation:{thread_id}:{datetime.now().timestamp()}"
                await self.redis_client.setex(
                    conv_key,
                    ttl,
                    json.dumps(conversation_data, default=str)
                )
                
                # Add to thread conversation list
                thread_key = f"thread_conversations:{thread_id}"
                await self.redis_client.lpush(thread_key, conv_key)
                await self.redis_client.expire(thread_key, ttl)
                
                # Maintain conversation history (keep last 20 exchanges)
                await self.redis_client.ltrim(thread_key, 0, 19)
                
                logger.debug("Conversation stored in short-term memory", 
                           thread_id=thread_id, ttl=ttl)
                return True
            else:
                # Fallback: log warning
                logger.warning("Redis unavailable, conversation not cached")
                return False
                
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            return False
    
    async def get_conversation_history(
        self,
        thread_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a thread"""
        
        try:
            if not self.redis_client:
                return []
            
            thread_key = f"thread_conversations:{thread_id}"
            conversation_keys = await self.redis_client.lrange(thread_key, 0, limit - 1)
            
            if not conversation_keys:
                return []
            
            # Get all conversations
            conversations = []
            for key in conversation_keys:
                conv_data = await self.redis_client.get(key)
                if conv_data:
                    try:
                        conversation = json.loads(conv_data)
                        conversations.append(conversation)
                    except json.JSONDecodeError:
                        continue
            
            # Sort by timestamp (newest first)
            conversations.sort(
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )
            
            logger.debug("Retrieved conversation history", 
                        thread_id=thread_id, count=len(conversations))
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    # Session State Methods
    
    async def store_session_state(
        self,
        session_id: str,
        state_data: Dict[str, Any],
        ttl: int = 1800  # 30 minutes default
    ) -> bool:
        """Store session state data"""
        
        try:
            if self.redis_client:
                session_key = f"session:{session_id}"
                await self.redis_client.setex(
                    session_key,
                    ttl,
                    json.dumps(state_data, default=str)
                )
                
                logger.debug("Session state stored", session_id=session_id, ttl=ttl)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to store session state: {e}")
            return False
    
    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session state data"""
        
        try:
            if not self.redis_client:
                return None
            
            session_key = f"session:{session_id}"
            state_data = await self.redis_client.get(session_key)
            
            if state_data:
                return json.loads(state_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session state: {e}")
            return None
    
    async def clear_session_state(self, session_id: str) -> bool:
        """Clear session state data"""
        
        try:
            if self.redis_client:
                session_key = f"session:{session_id}"
                deleted = await self.redis_client.delete(session_key)
                return deleted > 0
            return False
            
        except Exception as e:
            logger.error(f"Failed to clear session state: {e}")
            return False
    
    # Research Cache Methods
    
    async def cache_research_results(
        self,
        query_hash: str,
        results: Dict[str, Any],
        ttl: int = 3600  # 1 hour default
    ) -> bool:
        """Cache research results to avoid duplicate work"""
        
        try:
            if self.redis_client:
                cache_key = f"research_cache:{query_hash}"
                cache_data = {
                    "results": results,
                    "cached_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
                }
                
                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(cache_data, default=str)
                )
                
                logger.debug("Research results cached", query_hash=query_hash, ttl=ttl)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to cache research results: {e}")
            return False
    
    async def get_cached_research(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached research results"""
        
        try:
            if not self.redis_client:
                return None
            
            cache_key = f"research_cache:{query_hash}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                cache_info = json.loads(cached_data)
                return cache_info.get("results")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached research: {e}")
            return None
    
    # Workflow State Methods
    
    async def store_workflow_checkpoint(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        ttl: int = 86400  # 24 hours default
    ) -> bool:
        """Store workflow checkpoint for resuming interrupted workflows"""
        
        try:
            if self.redis_client:
                checkpoint_key = f"workflow_checkpoint:{workflow_id}"
                checkpoint_data = {
                    "state": state,
                    "checkpoint_time": datetime.now().isoformat(),
                    "workflow_id": workflow_id
                }
                
                await self.redis_client.setex(
                    checkpoint_key,
                    ttl,
                    json.dumps(checkpoint_data, default=str)
                )
                
                logger.debug("Workflow checkpoint stored", 
                           workflow_id=workflow_id, ttl=ttl)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to store workflow checkpoint: {e}")
            return False
    
    async def get_workflow_checkpoint(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow checkpoint"""
        
        try:
            if not self.redis_client:
                return None
            
            checkpoint_key = f"workflow_checkpoint:{workflow_id}"
            checkpoint_data = await self.redis_client.get(checkpoint_key)
            
            if checkpoint_data:
                checkpoint_info = json.loads(checkpoint_data)
                return checkpoint_info.get("state")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get workflow checkpoint: {e}")
            return None
    
    # Utility Methods
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        
        try:
            if not self.redis_client:
                return {"status": "unavailable"}
            
            # Get Redis info
            info = await self.redis_client.info("memory")
            
            # Count our keys
            pattern_counts = {}
            patterns = [
                "conversation:*",
                "thread_conversations:*", 
                "session:*",
                "research_cache:*",
                "workflow_checkpoint:*"
            ]
            
            for pattern in patterns:
                keys = await self.redis_client.keys(pattern)
                pattern_counts[pattern] = len(keys)
            
            return {
                "status": "available",
                "redis_memory_used": info.get("used_memory_human", "Unknown"),
                "redis_memory_peak": info.get("used_memory_peak_human", "Unknown"),
                "key_counts": pattern_counts,
                "total_keys": sum(pattern_counts.values())
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cleanup_expired_keys(self) -> Dict[str, int]:
        """Manually cleanup expired keys (Redis should handle this automatically)"""
        
        try:
            if not self.redis_client:
                return {"cleaned": 0}
            
            # This is mainly for monitoring - Redis handles expiration automatically
            # But we can check for orphaned thread conversation lists
            
            cleaned_count = 0
            thread_keys = await self.redis_client.keys("thread_conversations:*")
            
            for thread_key in thread_keys:
                # Check if any conversations in the list still exist
                conv_keys = await self.redis_client.lrange(thread_key, 0, -1)
                valid_keys = []
                
                for conv_key in conv_keys:
                    if await self.redis_client.exists(conv_key):
                        valid_keys.append(conv_key)
                    else:
                        cleaned_count += 1
                
                # Update the list with only valid keys
                if len(valid_keys) != len(conv_keys):
                    await self.redis_client.delete(thread_key)
                    if valid_keys:
                        await self.redis_client.lpush(thread_key, *valid_keys)
            
            logger.info(f"Cleaned up {cleaned_count} expired conversation references")
            
            return {"cleaned": cleaned_count}
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired keys: {e}")
            return {"cleaned": 0, "error": str(e)}


# Global instance
_short_term_memory: Optional[ShortTermMemory] = None

async def get_short_term_memory() -> ShortTermMemory:
    """Get or create short-term memory instance"""
    global _short_term_memory
    
    if _short_term_memory is None:
        _short_term_memory = ShortTermMemory()
        await _short_term_memory.initialize()
    
    return _short_term_memory