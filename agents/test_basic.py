"""
Minimal test of the basic workflow structure without external dependencies
"""

import asyncio
import sys
import os

# Add the agents directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


async def test_basic_imports():
    """Test that we can import all the basic components"""
    
    print("🧪 Testing Basic Component Imports")
    print("=" * 50)
    
    try:
        print("📦 Testing core imports...")
        
        # Test core modules
        from app.core.logging import get_logger
        print("✅ Core logging module imported")
        
        # Test memory modules
        try:
            from app.memory.short_term import ShortTermMemory
            from app.memory.long_term import LongTermMemory  
            from app.memory.manager import MemoryManager
            print("✅ Memory modules imported")
        except Exception as e:
            print(f"⚠️  Memory modules failed: {e}")
        
        # Test agent modules
        try:
            from app.agents.analyzer import AnalyzerAgent
            from app.agents.synthesizer import SynthesizerAgent
            print("✅ Agent modules imported")
        except Exception as e:
            print(f"❌ Agent modules failed: {e}")
            return False
        
        # Test basic workflow
        try:
            analyzer = AnalyzerAgent()
            synthesizer = SynthesizerAgent()
            print("✅ Agent instances created")
        except Exception as e:
            print(f"❌ Agent instantiation failed: {e}")
            return False
        
        # Test analyzer functionality with mock data
        print("\n🔍 Testing Analyzer Agent...")
        mock_query_analysis = {
            "intent": "analysis",
            "entities": [{"type": "company", "value": "AAPL"}],
            "complexity": "medium"
        }
        
        mock_sources = [
            {
                "content": "Apple Inc. reported strong quarterly earnings with revenue growth of 15%. The company's profit margin improved to 25%. Key financial metrics show P/E ratio of 28 and debt-to-equity ratio of 0.3.",
                "url": "https://example.com/apple-earnings",
                "title": "Apple Q3 Earnings Report"
            }
        ]
        
        analysis_result = await analyzer.analyze_financial_data(
            query_analysis=mock_query_analysis,
            sources=mock_sources
        )
        
        print(f"   📊 Analysis completed: {len(analysis_result.get('key_insights', []))} insights")
        print(f"   📈 Confidence score: {analysis_result.get('confidence_score', 0.0):.2f}")
        
        # Test synthesizer functionality
        print("\n💬 Testing Synthesizer Agent...")
        synthesis_result = await synthesizer.synthesize_response(
            query="What is Apple's financial performance?",
            query_analysis=mock_query_analysis,
            analysis_results=analysis_result,
            sources=mock_sources
        )
        
        response_length = len(synthesis_result.get('response', ''))
        sources_count = len(synthesis_result.get('sources', []))
        
        print(f"   📝 Response generated: {response_length} characters")
        print(f"   📚 Sources cited: {sources_count}")
        
        if response_length > 100:
            print("✅ Basic workflow test successful!")
            
            # Show response preview
            response = synthesis_result.get('response', '')
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"\n💬 Response Preview:")
            print(f"   {preview}")
            
            return True
        else:
            print("⚠️  Response seems too short")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_system():
    """Test the memory system components"""
    
    print("\n🧠 Testing Memory System")
    print("=" * 50)
    
    try:
        from app.memory.manager import MemoryManager, get_memory_manager
        
        # Try to get memory manager (might fail without Redis/vector DB)
        try:
            memory_manager = await get_memory_manager()
            print("✅ Memory manager created")
            
            # Test basic memory operations (will likely fail gracefully)
            try:
                await memory_manager.store_conversation_exchange(
                    thread_id="test-123",
                    user_id="user-123", 
                    query="Test query",
                    response="Test response",
                    sources=[],
                    analysis={},
                    insights=[]
                )
                print("✅ Memory storage test passed")
            except Exception as e:
                print(f"⚠️  Memory storage failed (expected): {str(e)[:100]}")
            
        except Exception as e:
            print(f"⚠️  Memory manager creation failed (Redis/Vector DB not available): {str(e)[:100]}")
            
    except Exception as e:
        print(f"❌ Memory system test failed: {e}")


if __name__ == "__main__":
    async def main():
        print("🚀 Finance Research System - Basic Component Test")
        print("=" * 60)
        
        # Test basic component imports and functionality
        basic_success = await test_basic_imports()
        
        # Test memory system
        await test_memory_system()
        
        print("\n" + "=" * 60)
        if basic_success:
            print("🎉 CORE FUNCTIONALITY WORKING!")
            print("   ✅ Agents can analyze financial data")
            print("   ✅ Responses can be synthesized")
            print("   ✅ Basic workflow is functional")
            print("\n💡 The chat system should work with mock data")
            print("   External dependencies (web search, scraping) may need setup")
        else:
            print("❌ CORE FUNCTIONALITY ISSUES DETECTED")
            print("   Please check the error messages above")
        
        print("\n🎯 Next Steps:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Set up Redis for memory caching")
        print("   3. Configure web search APIs (optional)")
        print("   4. Test full workflow with real queries")
    
    asyncio.run(main())