"""
Long-term memory implementation using vector database
Handles persistent insights, facts, and knowledge storage
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LongTermMemory:
    """
    Long-term memory for persistent knowledge storage
    Uses vector databases for semantic search and retrieval
    """
    
    def __init__(self):
        self.embedding_model = None
        self.vector_db = None
        self.vector_db_type = None
        self.fallback_storage = {}  # In-memory fallback
        
    async def initialize(self):
        """Initialize vector database and embedding model"""
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Embedding model initialized")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
        
        # Initialize vector database
        await self._initialize_vector_db()
    
    async def _initialize_vector_db(self):
        """Initialize vector database (Pinecone or ChromaDB)"""
        
        # Try Pinecone first
        if PINECONE_AVAILABLE and settings.pinecone_api_key and settings.pinecone_api_key != "your_pinecone_api_key_here":
            try:
                # Try new Pinecone v3 API first
                try:
                    from pinecone import Pinecone
                    # New v3 API
                    pc = Pinecone(api_key=settings.pinecone_api_key)
                    
                    # Check if index exists
                    existing_indexes = [index.name for index in pc.list_indexes()]
                    
                    if settings.pinecone_index_name not in existing_indexes:
                        # Create index if it doesn't exist (new v3 API format)
                        from pinecone import ServerlessSpec
                        pc.create_index(
                            name=settings.pinecone_index_name,
                            dimension=384,
                            metric="cosine",
                            spec=ServerlessSpec(
                                cloud="aws",
                                region="us-east-1"
                            )
                        )
                        logger.info("Created new Pinecone index", index_name=settings.pinecone_index_name)
                    
                    self.vector_db = pc.Index(settings.pinecone_index_name)
                    
                except ImportError:
                    # Fallback to older API
                    pinecone.init(
                        api_key=settings.pinecone_api_key,
                        environment=settings.pinecone_environment or "gcp-starter"
                    )
                    
                    # Create or get index
                    index_name = settings.pinecone_index_name
                    if index_name not in pinecone.list_indexes():
                        pinecone.create_index(
                            name=index_name,
                            dimension=384,  # all-MiniLM-L6-v2 dimension
                            metric="cosine"
                        )
                    
                    self.vector_db = pinecone.Index(index_name)
                
                self.vector_db_type = "pinecone"
                logger.info("✅ Pinecone vector database initialized successfully", 
                           index_name=settings.pinecone_index_name)
                return
                
            except Exception as e:
                logger.warning(f"Pinecone initialization failed: {e}")
        else:
            if not PINECONE_AVAILABLE:
                logger.info("Pinecone client not available")
            elif not settings.pinecone_api_key or settings.pinecone_api_key == "your_pinecone_api_key_here":
                logger.info("Pinecone API key not configured")
        
        # Try ChromaDB as fallback
        if CHROMADB_AVAILABLE:
            try:
                self.vector_db = chromadb.Client()
                # Create or get collection
                try:
                    self.collection = self.vector_db.create_collection(
                        name="finance_research_memory",
                        metadata={"hnsw:space": "cosine"}
                    )
                except ValueError:
                    # Collection already exists
                    self.collection = self.vector_db.get_collection(
                        name="finance_research_memory"
                    )
                
                self.vector_db_type = "chromadb"
                logger.info("✅ ChromaDB vector database initialized")
                return
                
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}")
        
        # Fallback to in-memory storage
        logger.warning("Using in-memory fallback for long-term memory")
        self.vector_db_type = "memory"
    
    def _create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding for text"""
        if not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return None
    
    def _create_memory_id(self, content: str, user_id: str) -> str:
        """Create unique ID for memory entry"""
        content_hash = hashlib.md5(f"{user_id}:{content}".encode()).hexdigest()
        return f"memory_{content_hash}"
    
    # Core Memory Methods
    
    async def store_insight(
        self,
        user_id: str,
        content: str,
        insight_type: str = "general",
        entities: List[str] = None,
        confidence: float = 1.0,
        thread_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Store a financial insight or fact"""
        
        try:
            memory_id = self._create_memory_id(content, user_id)
            
            memory_data = {
                "id": memory_id,
                "user_id": user_id,
                "thread_id": thread_id,
                "content": content,
                "type": insight_type,
                "entities": entities or [],
                "confidence": confidence,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "access_count": 0,
                "last_accessed": datetime.now().isoformat()
            }
            
            # Create embedding
            embedding = self._create_embedding(content)
            
            # Store in vector database
            if self.vector_db_type == "pinecone" and embedding:
                self.vector_db.upsert([
                    (memory_id, embedding, memory_data)
                ])
                
            elif self.vector_db_type == "chromadb" and embedding:
                self.collection.upsert(
                    ids=[memory_id],
                    embeddings=[embedding],
                    metadatas=[memory_data],
                    documents=[content]
                )
                
            else:
                # Fallback to in-memory storage
                self.fallback_storage[memory_id] = {
                    "embedding": embedding,
                    "data": memory_data
                }
            
            logger.debug("Insight stored in long-term memory",
                        memory_id=memory_id, type=insight_type)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store insight: {e}")
            return False
    
    async def store_insights(
        self,
        user_id: str,
        thread_id: str,
        insights: List[Dict[str, Any]],
        entities: List[str] = None
    ) -> int:
        """Store multiple insights from analysis results"""
        
        stored_count = 0
        
        for insight in insights:
            content = insight.get("content", "")
            insight_type = insight.get("type", "analysis")
            confidence = insight.get("confidence", 1.0)
            
            if content:
                success = await self.store_insight(
                    user_id=user_id,
                    content=content,
                    insight_type=insight_type,
                    entities=entities,
                    confidence=confidence,
                    thread_id=thread_id,
                    metadata=insight.get("metadata", {})
                )
                
                if success:
                    stored_count += 1
        
        logger.info(f"Stored {stored_count}/{len(insights)} insights")
        return stored_count
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
        min_confidence: float = 0.5,
        memory_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories using semantic similarity"""
        
        try:
            query_embedding = self._create_embedding(query)
            
            if not query_embedding:
                return []
            
            memories = []
            
            if self.vector_db_type == "pinecone":
                # Search in Pinecone
                results = self.vector_db.query(
                    vector=query_embedding,
                    top_k=limit,
                    include_metadata=True,
                    filter={"user_id": user_id}
                )
                
                for match in results.matches:
                    if match.score >= min_confidence:
                        memory = match.metadata
                        memory["similarity_score"] = match.score
                        memories.append(memory)
            
            elif self.vector_db_type == "chromadb":
                # Search in ChromaDB
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where={"user_id": user_id}
                )
                
                if results["metadatas"]:
                    for i, metadata in enumerate(results["metadatas"][0]):
                        distance = results["distances"][0][i] if results["distances"] else 0
                        similarity = 1 - distance  # Convert distance to similarity
                        
                        if similarity >= min_confidence:
                            memory = metadata
                            memory["similarity_score"] = similarity
                            memories.append(memory)
            
            else:
                # Fallback search in memory
                for memory_id, memory_info in self.fallback_storage.items():
                    data = memory_info["data"]
                    if data["user_id"] != user_id:
                        continue
                    
                    # Simple text matching for fallback
                    content_lower = data["content"].lower()
                    query_lower = query.lower()
                    
                    if any(word in content_lower for word in query_lower.split()):
                        memory = data.copy()
                        memory["similarity_score"] = 0.8  # Fallback score
                        memories.append(memory)
            
            # Filter by memory types if specified
            if memory_types:
                memories = [m for m in memories if m.get("type") in memory_types]
            
            # Sort by similarity score
            memories.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
            
            # Update access counts
            for memory in memories:
                await self._update_access_count(memory["id"])
            
            logger.debug(f"Found {len(memories)} relevant memories for query")
            
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    async def get_user_insights(
        self,
        user_id: str,
        insight_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all insights for a user, optionally filtered by type"""
        
        try:
            insights = []
            
            if self.vector_db_type == "pinecone":
                # Query all memories for user
                results = self.vector_db.query(
                    vector=[0.0] * 384,  # Dummy vector to get all results
                    top_k=limit,
                    include_metadata=True,
                    filter={"user_id": user_id}
                )
                
                for match in results.matches:
                    insight = match.metadata
                    if not insight_type or insight.get("type") == insight_type:
                        insights.append(insight)
            
            elif self.vector_db_type == "chromadb":
                # Get all memories for user
                results = self.collection.get(
                    where={"user_id": user_id},
                    limit=limit
                )
                
                if results["metadatas"]:
                    for metadata in results["metadatas"]:
                        if not insight_type or metadata.get("type") == insight_type:
                            insights.append(metadata)
            
            else:
                # Fallback: search in memory
                for memory_info in self.fallback_storage.values():
                    data = memory_info["data"]
                    if data["user_id"] == user_id:
                        if not insight_type or data.get("type") == insight_type:
                            insights.append(data)
            
            # Sort by creation date (newest first)
            insights.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )
            
            return insights[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get user insights: {e}")
            return []
    
    async def _update_access_count(self, memory_id: str) -> bool:
        """Update access count and last accessed time for a memory"""
        
        try:
            if self.vector_db_type == "pinecone":
                # Pinecone doesn't support in-place updates easily
                # This would require fetching, updating, and re-upserting
                pass
            
            elif self.vector_db_type == "chromadb":
                # ChromaDB also has limitations for metadata updates
                # Would need to fetch and re-upsert
                pass
            
            else:
                # Update in fallback storage
                if memory_id in self.fallback_storage:
                    memory_data = self.fallback_storage[memory_id]["data"]
                    memory_data["access_count"] = memory_data.get("access_count", 0) + 1
                    memory_data["last_accessed"] = datetime.now().isoformat()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update access count: {e}")
            return False
    
    # Utility Methods
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get long-term memory statistics"""
        
        try:
            stats = {
                "vector_db_type": self.vector_db_type,
                "embedding_model": "all-MiniLM-L6-v2" if self.embedding_model else None,
                "total_memories": 0,
                "memory_types": {},
                "oldest_memory": None,
                "newest_memory": None
            }
            
            if self.vector_db_type == "pinecone":
                # Pinecone stats are limited
                stats["total_memories"] = "unknown"
                
            elif self.vector_db_type == "chromadb":
                # Get collection info
                collection_info = self.collection.count()
                stats["total_memories"] = collection_info
                
            else:
                # Fallback storage stats
                stats["total_memories"] = len(self.fallback_storage)
                
                # Analyze memory types
                for memory_info in self.fallback_storage.values():
                    data = memory_info["data"]
                    memory_type = data.get("type", "unknown")
                    stats["memory_types"][memory_type] = stats["memory_types"].get(memory_type, 0) + 1
                    
                    # Track date ranges
                    created_at = data.get("created_at")
                    if created_at:
                        if not stats["oldest_memory"] or created_at < stats["oldest_memory"]:
                            stats["oldest_memory"] = created_at
                        if not stats["newest_memory"] or created_at > stats["newest_memory"]:
                            stats["newest_memory"] = created_at
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_memories(
        self,
        user_id: str,
        days_old: int = 90,
        min_access_count: int = 0
    ) -> int:
        """Clean up old, unused memories"""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cutoff_str = cutoff_date.isoformat()
            
            cleaned_count = 0
            
            if self.vector_db_type == "memory":
                # Only implemented for fallback storage
                to_delete = []
                
                for memory_id, memory_info in self.fallback_storage.items():
                    data = memory_info["data"]
                    
                    if (data["user_id"] == user_id and
                        data.get("created_at", "") < cutoff_str and
                        data.get("access_count", 0) <= min_access_count):
                        to_delete.append(memory_id)
                
                for memory_id in to_delete:
                    del self.fallback_storage[memory_id]
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} old memories for user {user_id}")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old memories: {e}")
            return 0


# Global instance
_long_term_memory: Optional[LongTermMemory] = None

async def get_long_term_memory() -> LongTermMemory:
    """Get or create long-term memory instance"""
    global _long_term_memory
    
    if _long_term_memory is None:
        _long_term_memory = LongTermMemory()
        await _long_term_memory.initialize()
    
    return _long_term_memory