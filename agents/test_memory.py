"""
Memory system test script
Run this to validate that the memory modules are working correctly
"""

import asyncio
import json
from datetime import datetime

from app.memory.manager import get_memory_manager
from app.core.logging import setup_logging

# Setup logging
setup_logging()


async def test_memory_system():
    """Test the memory system functionality"""
    
    print("🧠 Testing Finance Research Agent Memory System")
    print("=" * 50)
    
    try:
        # Initialize memory manager
        print("1. Initializing memory manager...")
        memory_manager = await get_memory_manager()
        print("   ✅ Memory manager initialized")
        
        # Test short-term memory (conversation storage)
        print("\n2. Testing short-term memory...")
        test_thread_id = "test_thread_001"
        test_user_id = "test_user_001"
        
        conversation_stored = await memory_manager.store_conversation_exchange(
            thread_id=test_thread_id,
            user_id=test_user_id,
            query="What is Apple's P/E ratio?",
            response="Apple's current P/E ratio is approximately 28.5, which indicates...",
            sources=[
                {"url": "https://finance.yahoo.com/quote/AAPL", "title": "Apple Stock Info"},
                {"url": "https://seekingalpha.com/symbol/AAPL", "title": "Apple Analysis"}
            ],
            analysis={"confidence": 0.9, "data_quality": "high"},
            insights=[
                {
                    "content": "Apple's P/E ratio of 28.5 is higher than tech sector average",
                    "type": "valuation",
                    "confidence": 0.85
                }
            ]
        )
        
        if conversation_stored:
            print("   ✅ Conversation stored successfully")
        else:
            print("   ⚠️  Conversation storage failed (may be using fallback)")
        
        # Test conversation retrieval
        print("\n3. Testing conversation context retrieval...")
        context = await memory_manager.get_conversation_context(
            thread_id=test_thread_id,
            user_id=test_user_id
        )
        
        print(f"   📊 Retrieved context:")
        print(f"      - History length: {context['context_summary']['history_length']}")
        print(f"      - Insights found: {context['context_summary']['insights_found']}")
        
        # Test long-term memory (insights search)
        print("\n4. Testing long-term memory...")
        if memory_manager.long_term:
            # Store an additional insight
            insight_stored = await memory_manager.long_term.store_insight(
                user_id=test_user_id,
                content="Apple shows strong revenue growth in services segment",
                insight_type="financial_trend",
                entities=["Apple", "AAPL", "services"],
                confidence=0.9
            )
            
            if insight_stored:
                print("   ✅ Insight stored in long-term memory")
                
                # Search for related insights
                related_insights = await memory_manager.long_term.search_memories(
                    user_id=test_user_id,
                    query="Apple financial performance",
                    limit=5
                )
                
                print(f"   🔍 Found {len(related_insights)} related insights")
                for insight in related_insights:
                    print(f"      - {insight.get('content', 'N/A')[:50]}...")
            else:
                print("   ⚠️  Long-term memory using fallback storage")
        else:
            print("   ⚠️  Long-term memory not available")
        
        # Test user knowledge profile
        print("\n5. Testing user knowledge profile...")
        profile = await memory_manager.build_user_knowledge_profile(test_user_id)
        
        print(f"   👤 User Profile:")
        print(f"      - Interests: {len(profile['interests'])}")
        print(f"      - Expertise areas: {len(profile['expertise_areas'])}")
        print(f"      - Key insights: {len(profile['key_insights'])}")
        
        # Test memory health
        print("\n6. Testing memory system health...")
        health_status = await memory_manager.get_memory_health_status()
        
        print(f"   🏥 Memory Health: {health_status['overall_status'].upper()}")
        print(f"      - Short-term: {health_status['short_term_memory'].get('status', 'unknown')}")
        print(f"      - Long-term: {health_status['long_term_memory'].get('vector_db_type', 'unknown')}")
        
        if health_status.get('recommendations'):
            print(f"      - Recommendations: {', '.join(health_status['recommendations'])}")
        
        # Test research caching
        print("\n7. Testing research caching...")
        research_cached = await memory_manager.store_research_session(
            session_id="test_research_001",
            user_id=test_user_id,
            query="Tesla stock analysis",
            research_results={
                "summary": "Tesla shows volatile but generally positive trends",
                "key_metrics": {"pe_ratio": 65.2, "market_cap": "800B"},
                "recommendation": "Hold"
            },
            key_insights=[
                {
                    "content": "Tesla's high P/E ratio reflects growth expectations",
                    "type": "valuation_insight",
                    "confidence": 0.8
                }
            ]
        )
        
        if research_cached:
            print("   ✅ Research session cached")
            
            # Try to retrieve cached research
            cached_result = await memory_manager.get_cached_research(
                user_id=test_user_id,
                query="Tesla stock analysis"
            )
            
            if cached_result:
                print("   ✅ Cached research retrieved successfully")
            else:
                print("   ⚠️  Cached research not found (may have expired)")
        else:
            print("   ⚠️  Research caching failed")
        
        print("\n" + "=" * 50)
        print("🎉 Memory system test completed!")
        print("\n📋 Summary:")
        print(f"   - Overall Status: {health_status['overall_status'].upper()}")
        print(f"   - Short-term Memory: {'✅' if health_status['short_term_memory'].get('status') == 'available' else '⚠️'}")
        print(f"   - Long-term Memory: {'✅' if health_status['long_term_memory'].get('vector_db_type') else '⚠️'}")
        print(f"   - Memory Manager: ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_memory_system())
    exit(0 if success else 1)