"""
Test Pinecone integration with the provided API key
"""

import asyncio
import sys
import os

# Add the agents directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.memory.long_term import LongTermMemory
from app.core.logging import get_logger

logger = get_logger(__name__)


async def test_pinecone_integration():
    """Test Pinecone vector database integration"""
    
    print("🧪 Testing Pinecone Integration")
    print("=" * 50)
    
    try:
        # Create long-term memory instance
        print("📦 Initializing long-term memory...")
        memory = LongTermMemory()
        await memory.initialize()
        
        # Check which vector database was initialized
        if hasattr(memory, 'vector_db_type'):
            print(f"✅ Vector database type: {memory.vector_db_type}")
            
            if memory.vector_db_type == "pinecone":
                print("🎯 Pinecone successfully initialized!")
                
                # Test storing an insight
                print("\n🔍 Testing insight storage...")
                
                await memory.store_insight(
                    user_id="test-user-001",
                    content="Apple Inc. reported strong Q3 earnings with 15% revenue growth and improved profit margins.",
                    insight_type="earnings",
                    entities=["Apple Inc.", "AAPL"],
                    confidence=0.85,
                    metadata={"revenue_growth": "15%", "profit_margin": "25%", "quarter": "Q3"}
                )
                print("✅ Insight stored successfully")
                
                # Test searching for insights
                print("\n🔎 Testing insight search...")
                search_results = await memory.search_memories(
                    query="Apple earnings performance",
                    user_id="test-user-001",
                    limit=5
                )
                
                print(f"📊 Search results: {len(search_results)} insights found")
                
                if search_results:
                    for i, result in enumerate(search_results[:2], 1):
                        similarity = result.get('similarity', 0.0)
                        content = result.get('content', '')[:100]
                        print(f"   {i}. Similarity: {similarity:.3f} - {content}...")
                
                print("✅ Pinecone integration test completed successfully!")
                return True
                
            elif memory.vector_db_type == "chromadb":
                print("⚠️  Using ChromaDB fallback (Pinecone not available)")
                return False
            elif memory.vector_db_type == "memory":
                print("⚠️  Using in-memory fallback (no vector DB available)")
                return False
            else:
                print(f"❓ Unknown vector database type: {memory.vector_db_type}")
                return False
        else:
            print("❌ No vector database initialized")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_with_pinecone():
    """Test the complete memory system with Pinecone"""
    
    print("\n🧠 Testing Complete Memory System with Pinecone")
    print("=" * 60)
    
    try:
        from app.memory.manager import get_memory_manager
        
        # Get memory manager
        print("📦 Initializing memory manager...")
        memory_manager = await get_memory_manager()
        print("✅ Memory manager initialized")
        
        # Test storing a conversation exchange
        print("\n💬 Testing conversation storage...")
        await memory_manager.store_conversation_exchange(
            thread_id="test-pinecone-001",
            user_id="test-user-001",
            query="What is Apple's financial performance in Q3?",
            response="Apple reported strong Q3 performance with 15% revenue growth and improved margins.",
            sources=[
                {"title": "Apple Q3 Earnings", "url": "https://apple.com/earnings", "domain": "apple.com"}
            ],
            analysis={
                "key_insights": ["Strong revenue growth", "Improved profit margins"],
                "confidence_score": 0.85
            },
            insights=["Revenue growth of 15%", "Profit margin improvement"]
        )
        print("✅ Conversation exchange stored")
        
        # Test getting conversation context
        print("\n📖 Testing conversation context retrieval...")
        context = await memory_manager.get_conversation_context(
            thread_id="test-pinecone-001",
            user_id="test-user-001",
            max_history=5
        )
        
        print(f"📊 Context retrieved: {len(context.get('recent_messages', []))} messages")
        print(f"📈 Relevant insights: {len(context.get('relevant_insights', []))}")
        
        # Test building user knowledge profile
        print("\n👤 Testing user knowledge profile...")
        profile = await memory_manager.build_user_knowledge_profile(
            user_id="test-user-001",
            limit=10
        )
        
        print(f"📊 User profile: {len(profile.get('topics', []))} topics")
        print(f"📈 Total interactions: {profile.get('total_interactions', 0)}")
        
        if profile.get('topics'):
            print("   Top topics:")
            for topic in profile['topics'][:3]:
                print(f"     - {topic}")
        
        print("✅ Complete memory system test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Memory system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Pinecone Integration Test Suite")
        print("=" * 60)
        
        # Test basic Pinecone integration
        pinecone_success = await test_pinecone_integration()
        
        # Test complete memory system if Pinecone works
        if pinecone_success:
            memory_success = await test_memory_with_pinecone()
        else:
            print("\n⏭️  Skipping memory system test (Pinecone not available)")
            memory_success = False
        
        print("\n" + "=" * 60)
        print("🎯 TEST RESULTS:")
        print(f"   Pinecone Integration: {'✅ PASS' if pinecone_success else '❌ FAIL'}")
        print(f"   Memory System: {'✅ PASS' if memory_success else '❌ FAIL'}")
        
        if pinecone_success and memory_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("   Your Pinecone API key is working correctly")
            print("   The vector database is ready for production use")
        elif pinecone_success:
            print("\n⚠️  PARTIAL SUCCESS")
            print("   Pinecone API key works, but memory system needs attention")
        else:
            print("\n❌ TESTS FAILED")
            print("   Please check your Pinecone API key and configuration")
        
        print("\n💡 Configuration Status:")
        from app.core.config import settings
        print(f"   API Key Present: {'✅' if settings.pinecone_api_key else '❌'}")
        print(f"   Environment: {settings.pinecone_environment or 'gcp-starter'}")
        print(f"   Index Name: {settings.pinecone_index_name}")
    
    asyncio.run(main())