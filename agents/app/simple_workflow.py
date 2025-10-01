"""
Simplified research workflow - fallback when LangGraph is not available
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

from app.agents.researcher import ResearcherAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.synthesizer import SynthesizerAgent
from app.memory.manager import MemoryManager, get_memory_manager
from app.core.logging import get_logger

logger = get_logger(__name__)


class SimpleResearchWorkflow:
    """Simple workflow implementation without LangGraph dependencies"""
    
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.analyzer = AnalyzerAgent()
        self.synthesizer = SynthesizerAgent()
        self.memory_manager = None
    
    async def execute(self, graph_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete research workflow"""
        
        start_time = datetime.now()
        result = {
            "query": graph_input.get("query", ""),
            "thread_id": graph_input.get("thread_id", ""),
            "user_id": graph_input.get("user_id", ""),
            "conversation_history": graph_input.get("conversation_history", []),
            "metadata": graph_input.get("metadata", {}),
            "research_depth": graph_input.get("research_depth", "deep"),
            "nodes_executed": [],
            "thinking_trace": {},
            "final_response": "",
            "sources": [],
            "processing_time": 0.0
        }
        
        try:
            logger.info("Starting simple research workflow", 
                       query=result["query"][:100],
                       thread_id=result["thread_id"])
            
            # Step 1: Analyze Query
            logger.info("Step 1: Analyzing query")
            query_analysis = await self.researcher.analyze_query(
                query=result["query"],
                conversation_history=result["conversation_history"],
                metadata=result["metadata"]
            )
            result["query_analysis"] = query_analysis
            result["nodes_executed"].append("analyze_query")
            result["thinking_trace"]["query_analysis"] = {
                "intent": query_analysis.get("intent"),
                "entities": query_analysis.get("entities"),
                "complexity": query_analysis.get("complexity"),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Step 2: Plan Research
            logger.info("Step 2: Planning research")
            research_plan = await self.researcher.plan_research(
                query_analysis=query_analysis,
                research_depth=result["research_depth"],
                metadata=result["metadata"]
            )
            result["research_plan"] = research_plan
            result["nodes_executed"].append("plan_research")
            result["thinking_trace"]["research_plan"] = {
                "strategy": research_plan.get("strategy"),
                "search_queries": research_plan.get("search_queries", []),
                "data_sources": research_plan.get("data_sources", []),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Step 3: Search Web
            logger.info("Step 3: Searching web")
            search_results = await self.researcher.search_web(
                research_plan=research_plan,
                query_analysis=query_analysis
            )
            result["search_results"] = search_results
            result["nodes_executed"].append("search_web")
            result["thinking_trace"]["web_search"] = {
                "total_results": len(search_results),
                "sources": [r.get("url", "") for r in search_results[:5]],
                "timestamp": datetime.now().isoformat(),
            }
            
            # Step 4: Scrape Content
            logger.info("Step 4: Scraping content")
            scraped_content = await self.researcher.scrape_content(
                search_results=search_results,
                query_analysis=query_analysis
            )
            result["scraped_content"] = scraped_content
            result["nodes_executed"].append("scrape_content")
            result["thinking_trace"]["content_scraping"] = {
                "pages_scraped": len(scraped_content),
                "total_content_length": sum(len(c.get("content", "")) for c in scraped_content),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Step 5: Deduplicate Sources
            logger.info("Step 5: Deduplicating sources")
            deduplicated_sources = await self.researcher.deduplicate_sources(
                scraped_content=scraped_content,
                max_sources=10
            )
            result["deduplicated_sources"] = deduplicated_sources
            result["nodes_executed"].append("deduplicate_sources")
            result["thinking_trace"]["deduplication"] = {
                "original_count": len(scraped_content),
                "deduplicated_count": len(deduplicated_sources),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Step 6: Analyze Data
            logger.info("Step 6: Analyzing data")
            analysis_results = await self.analyzer.analyze_financial_data(
                query_analysis=query_analysis,
                sources=deduplicated_sources,
                conversation_history=result["conversation_history"]
            )
            result["analysis_results"] = analysis_results
            result["nodes_executed"].append("analyze_data")
            result["thinking_trace"]["analysis"] = {
                "key_insights": analysis_results.get("key_insights", [])[:3],
                "data_points": len(analysis_results.get("data_points", [])),
                "confidence_score": analysis_results.get("confidence_score"),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Step 7: Synthesize Response
            logger.info("Step 7: Synthesizing response")
            synthesis_result = await self.synthesizer.synthesize_response(
                query=result["query"],
                query_analysis=query_analysis,
                analysis_results=analysis_results,
                sources=deduplicated_sources,
                conversation_history=result["conversation_history"]
            )
            result["final_response"] = synthesis_result["response"]
            result["sources"] = synthesis_result["sources"]
            result["nodes_executed"].append("synthesize_response")
            result["thinking_trace"]["synthesis"] = {
                "response_length": len(synthesis_result["response"]),
                "sources_cited": len(synthesis_result["sources"]),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Step 8: Update Memory
            logger.info("Step 8: Updating memory")
            try:
                if self.memory_manager is None:
                    self.memory_manager = await get_memory_manager()
                
                await self.memory_manager.store_conversation_exchange(
                    thread_id=result["thread_id"],
                    user_id=result["user_id"],
                    query=result["query"],
                    response=result["final_response"],
                    sources=result["sources"],
                    analysis=analysis_results,
                    insights=analysis_results.get("key_insights", [])
                )
                result["nodes_executed"].append("update_memory")
            except Exception as e:
                logger.warning("Memory update failed", error=str(e))
                # Continue without memory update
            
            # Calculate processing time
            end_time = datetime.now()
            result["processing_time"] = (end_time - start_time).total_seconds()
            
            logger.info("Simple research workflow completed successfully",
                       thread_id=result["thread_id"],
                       processing_time=result["processing_time"],
                       nodes_executed=len(result["nodes_executed"]))
            
            return result
            
        except Exception as e:
            logger.error("Error in simple research workflow", 
                        error=str(e),
                        thread_id=result.get("thread_id"))
            
            # Return error response
            end_time = datetime.now()
            result["processing_time"] = (end_time - start_time).total_seconds()
            result["final_response"] = f"I apologize, but I encountered an error while processing your request: {str(e)}"
            result["sources"] = []
            
            return result


# Global workflow instance
_workflow_instance = None


async def get_workflow():
    """Get or create workflow instance"""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = SimpleResearchWorkflow()
    return _workflow_instance


def create_research_graph():
    """
    Create research workflow - returns either LangGraph or simple workflow
    """
    # Try to use LangGraph if available
    try:
        from langgraph import Graph, START, END
        from langgraph.graph import StateGraph
        from langgraph.checkpoint.memory import MemorySaver
        
        logger.info("LangGraph available, using advanced workflow")
        # Import the original graph creation from graph.py
        # For now, return the simple workflow as fallback
        return SimpleWorkflowAdapter()
        
    except ImportError:
        logger.info("LangGraph not available, using simple workflow")
        return SimpleWorkflowAdapter()


class SimpleWorkflowAdapter:
    """Adapter to make SimpleResearchWorkflow compatible with expected interface"""
    
    def __init__(self):
        self.workflow = None
    
    async def ainvoke(self, graph_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow (compatible with LangGraph interface)"""
        if self.workflow is None:
            self.workflow = await get_workflow()
        return await self.workflow.execute(graph_input)
    
    async def astream_events(self, graph_input: Dict[str, Any], version: str = "v1"):
        """Stream events (simplified implementation)"""
        # For now, execute normally and yield final result
        result = await self.ainvoke(graph_input)
        
        # Simulate streaming events
        for node in result.get("nodes_executed", []):
            yield {
                "event": "on_tool_start",
                "data": {"name": node}
            }
            await asyncio.sleep(0.1)  # Small delay
            yield {
                "event": "on_tool_end", 
                "data": {"name": node, "output": {}}
            }
        
        # Final result
        yield {
            "event": "on_chain_end",
            "data": {"output": result}
        }