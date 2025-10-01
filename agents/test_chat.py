"""
Test the chat workflow to ensure it's working properly
"""

import asyncio
import sys
import os

# Add the agents directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.simple_workflow import create_research_graph
from app.core.logging import get_logger

logger = get_logger(__name__)


async def test_chat_workflow():
    """Test the complete chat workflow"""
    
    print("🚀 Testing Finance Research Chat Workflow")
    print("=" * 50)
    
    try:
        # Create the workflow
        print("📦 Creating research workflow...")
        graph = create_research_graph()
        print("✅ Workflow created successfully")
        
        # Test input
        test_input = {
            "query": "What is the current financial performance of Apple Inc?",
            "thread_id": "test-thread-001",
            "user_id": "test-user-001",
            "conversation_history": [],
            "metadata": {"research_depth": "medium"},
            "research_depth": "medium"
        }
        
        print(f"\n🔍 Testing query: '{test_input['query']}'")
        print("⏳ Processing request...")
        
        # Execute the workflow
        result = await graph.ainvoke(test_input)
        
        print("\n📊 Workflow Results:")
        print("-" * 30)
        print(f"Query: {result.get('query', 'N/A')}")
        print(f"Thread ID: {result.get('thread_id', 'N/A')}")
        print(f"Nodes Executed: {len(result.get('nodes_executed', []))}")
        print(f"Processing Time: {result.get('processing_time', 0):.2f} seconds")
        print(f"Final Response Length: {len(result.get('final_response', ''))}")
        print(f"Sources Found: {len(result.get('sources', []))}")
        
        # Show nodes executed
        nodes_executed = result.get('nodes_executed', [])
        if nodes_executed:
            print(f"\n📝 Workflow Steps Completed:")
            for i, node in enumerate(nodes_executed, 1):
                print(f"  {i}. {node}")
        
        # Show a preview of the response
        final_response = result.get('final_response', '')
        if final_response:
            print(f"\n💬 Response Preview:")
            preview = final_response[:300] + "..." if len(final_response) > 300 else final_response
            print(f"  {preview}")
        else:
            print("⚠️  No response generated")
        
        # Show sources
        sources = result.get('sources', [])
        if sources:
            print(f"\n📚 Sources ({len(sources)}):")
            for i, source in enumerate(sources[:3], 1):  # Show first 3 sources
                title = source.get('title', 'Unknown Title')
                url = source.get('url', 'No URL')
                print(f"  {i}. {title[:50]}{'...' if len(title) > 50 else ''}")
                print(f"     URL: {url}")
        
        # Check for errors
        if 'error' in result:
            print(f"\n❌ Error encountered: {result['error']}")
        elif final_response and len(final_response) > 50:
            print(f"\n✅ Test completed successfully!")
            print(f"   The workflow generated a {len(final_response)}-character response")
            print(f"   with {len(sources)} sources in {result.get('processing_time', 0):.2f} seconds")
        else:
            print(f"\n⚠️  Test completed but response seems incomplete")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        logger.error("Chat workflow test failed", error=str(e))
        import traceback
        print(f"\nFull traceback:")
        traceback.print_exc()
        return None


async def test_streaming_workflow():
    """Test the streaming workflow"""
    
    print("\n🎵 Testing Streaming Workflow")
    print("=" * 50)
    
    try:
        graph = create_research_graph()
        
        test_input = {
            "query": "What are the key financial metrics for Microsoft?",
            "thread_id": "test-stream-001",
            "user_id": "test-user-001",
            "conversation_history": [],
            "metadata": {"research_depth": "shallow", "streaming": True},
            "research_depth": "shallow"
        }
        
        print(f"🔍 Streaming query: '{test_input['query']}'")
        print("📡 Streaming events:")
        
        event_count = 0
        async for event in graph.astream_events(test_input, version="v1"):
            event_count += 1
            event_type = event.get("event", "unknown")
            event_data = event.get("data", {})
            
            if event_type == "on_tool_start":
                tool_name = event_data.get("name", "unknown")
                print(f"  🔧 Started: {tool_name}")
            elif event_type == "on_tool_end":
                tool_name = event_data.get("name", "unknown")
                print(f"  ✅ Completed: {tool_name}")
            elif event_type == "on_chain_end":
                output = event_data.get("output", {})
                response_length = len(output.get("final_response", ""))
                print(f"  🏁 Final result: {response_length} characters")
                break
        
        print(f"\n📊 Streaming completed with {event_count} events")
        
    except Exception as e:
        print(f"\n❌ Streaming test failed: {str(e)}")


if __name__ == "__main__":
    async def main():
        print("🧪 Finance Research Chat System Test")
        print("=" * 60)
        
        # Test regular workflow
        result = await test_chat_workflow()
        
        # Test streaming if regular workflow succeeded
        if result and result.get('final_response'):
            await test_streaming_workflow()
        else:
            print("\n⏭️  Skipping streaming test due to workflow issues")
        
        print("\n🎉 Testing completed!")
    
    asyncio.run(main())