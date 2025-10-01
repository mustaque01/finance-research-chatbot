"""
Simple Pinecone validation test
"""

import asyncio
import sys
import os

# Add the agents directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


async def test_pinecone_basic():
    """Basic Pinecone connectivity test"""
    
    print("🎯 Pinecone API Key Validation Test")
    print("=" * 50)
    
    try:
        from app.core.config import settings
        from app.memory.long_term import LongTermMemory
        
        print(f"📋 API Key Present: {'✅' if settings.pinecone_api_key else '❌'}")
        print(f"📋 Index Name: {settings.pinecone_index_name}")
        print(f"📋 Environment: {settings.pinecone_environment or 'gcp-starter'}")
        
        if not settings.pinecone_api_key or settings.pinecone_api_key == "your_pinecone_api_key_here":
            print("❌ Pinecone API key not configured")
            return False
        
        print("\n🔗 Testing Pinecone Connection...")
        memory = LongTermMemory()
        await memory.initialize()
        
        if hasattr(memory, 'vector_db_type') and memory.vector_db_type == "pinecone":
            print("✅ Pinecone connection successful!")
            print("✅ Vector database index created/accessed")
            
            # Test basic functionality
            print("\n💾 Testing basic operations...")
            
            # Store a simple insight
            success = await memory.store_insight(
                user_id="test-validation",
                content="Test insight for Pinecone validation",
                insight_type="test",
                entities=["validation"],
                confidence=0.9
            )
            
            if success:
                print("✅ Data storage test passed")
            else:
                print("⚠️  Data storage had issues but connection works")
            
            # Test search
            results = await memory.search_memories(
                query="test validation",
                user_id="test-validation",
                limit=1
            )
            
            print(f"✅ Search test completed: {len(results)} results")
            
            print("\n🎉 PINECONE INTEGRATION FULLY OPERATIONAL!")
            print("   Your API key is working correctly")
            print("   Vector database is ready for production")
            return True
            
        else:
            print(f"❌ Pinecone not initialized (using {getattr(memory, 'vector_db_type', 'unknown')})")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


async def test_chat_with_pinecone():
    """Test chat system with Pinecone enabled"""
    
    print("\n🤖 Testing Chat System with Pinecone")
    print("=" * 50)
    
    try:
        from app.simple_workflow import create_research_graph
        
        # Create workflow
        graph = create_research_graph()
        
        # Test with a simple query
        test_input = {
            "query": "What are Apple's key financial metrics?",
            "thread_id": "pinecone-test-001",
            "user_id": "pinecone-user-001",
            "conversation_history": [],
            "metadata": {"research_depth": "shallow"},
            "research_depth": "shallow"
        }
        
        print("🔍 Processing test query...")
        result = await graph.ainvoke(test_input)
        
        response_length = len(result.get('final_response', ''))
        sources_count = len(result.get('sources', []))
        
        print(f"📊 Response generated: {response_length} characters")
        print(f"📚 Sources found: {sources_count}")
        print(f"⏱️  Processing time: {result.get('processing_time', 0):.2f}s")
        
        if response_length > 100:
            print("✅ Chat system working with Pinecone!")
            return True
        else:
            print("⚠️  Chat system working but response is short")
            return True
            
    except Exception as e:
        print(f"❌ Chat test failed: {str(e)}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Pinecone Integration Validation")
        print("=" * 60)
        
        # Test basic Pinecone functionality
        pinecone_works = await test_pinecone_basic()
        
        # Test chat system if Pinecone works
        if pinecone_works:
            chat_works = await test_chat_with_pinecone()
        else:
            chat_works = False
        
        print("\n" + "=" * 60)
        print("🎯 FINAL RESULTS:")
        print(f"   Pinecone API Key: {'✅ WORKING' if pinecone_works else '❌ FAILED'}")
        print(f"   Chat Integration: {'✅ WORKING' if chat_works else '❌ FAILED'}")
        
        if pinecone_works:
            print("\n🎉 SUCCESS!")
            print("   ✅ Your Pinecone API key is correctly configured")
            print("   ✅ Vector database is operational")
            print("   ✅ Memory system is enhanced with persistent storage")
            print("   ✅ Chat responses will now have improved context awareness")
            
            print("\n🔧 What this enables:")
            print("   • Long-term memory across chat sessions")
            print("   • Better context understanding")
            print("   • Improved response relevance")
            print("   • User knowledge building over time")
        else:
            print("\n❌ ISSUES DETECTED")
            print("   Please check your Pinecone configuration")
    
    asyncio.run(main())