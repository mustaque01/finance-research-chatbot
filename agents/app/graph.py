"""
LangGraph workflow for finance research agent
"""

import asyncio
from typing import Dict, Any, List, TypedDict, Annotated
from datetime import datetime

from langgraph import Graph, START, END
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.agents.researcher import ResearcherAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.synthesizer import SynthesizerAgent
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.core.logging import get_logger

logger = get_logger(__name__)


class ResearchState(TypedDict):
    """State for the research workflow"""
    # Input
    query: str
    thread_id: str
    user_id: str
    conversation_history: List[BaseMessage]
    metadata: Dict[str, Any]
    research_depth: str
    
    # Workflow state
    query_analysis: Dict[str, Any]
    research_plan: Dict[str, Any]
    search_results: List[Dict[str, Any]]
    scraped_content: List[Dict[str, Any]]
    deduplicated_sources: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    final_response: str
    thinking_trace: Dict[str, Any]
    sources: List[Dict[str, Any]]
    
    # Metadata
    processing_time: float
    nodes_executed: List[str]


def create_research_graph():
    """Create the research workflow graph"""
    
    # Initialize components
    researcher = ResearcherAgent()
    analyzer = AnalyzerAgent()
    synthesizer = SynthesizerAgent()
    short_term_memory = ShortTermMemory()
    long_term_memory = LongTermMemory()
    
    async def analyze_query_node(state: ResearchState) -> ResearchState:
        """Analyze the user query to understand intent and requirements"""
        logger.info("Executing query analysis node", thread_id=state.get("thread_id"))
        
        start_time = datetime.now()
        
        try:
            query_analysis = await researcher.analyze_query(
                query=state["query"],
                conversation_history=state.get("conversation_history", []),
                metadata=state.get("metadata", {})
            )
            
            state["query_analysis"] = query_analysis
            state["nodes_executed"] = state.get("nodes_executed", []) + ["analyze_query"]
            
            # Update thinking trace
            thinking_trace = state.get("thinking_trace", {})
            thinking_trace["query_analysis"] = {
                "intent": query_analysis.get("intent"),
                "entities": query_analysis.get("entities"),
                "complexity": query_analysis.get("complexity"),
                "timestamp": datetime.now().isoformat(),
            }
            state["thinking_trace"] = thinking_trace
            
            logger.info("Query analysis completed", 
                       intent=query_analysis.get("intent"),
                       entities=len(query_analysis.get("entities", [])))
            
            return state
            
        except Exception as e:
            logger.error("Error in query analysis", error=str(e))
            state["query_analysis"] = {"error": str(e)}
            return state
    
    async def plan_research_node(state: ResearchState) -> ResearchState:
        """Plan the research strategy"""
        logger.info("Executing research planning node", thread_id=state.get("thread_id"))
        
        try:
            research_plan = await researcher.plan_research(
                query_analysis=state["query_analysis"],
                research_depth=state.get("research_depth", "deep"),
                metadata=state.get("metadata", {})
            )
            
            state["research_plan"] = research_plan
            state["nodes_executed"] = state.get("nodes_executed", []) + ["plan_research"]
            
            # Update thinking trace
            thinking_trace = state.get("thinking_trace", {})
            thinking_trace["research_plan"] = {
                "strategy": research_plan.get("strategy"),
                "search_queries": research_plan.get("search_queries", []),
                "data_sources": research_plan.get("data_sources", []),
                "timestamp": datetime.now().isoformat(),
            }
            state["thinking_trace"] = thinking_trace
            
            logger.info("Research planning completed",
                       strategy=research_plan.get("strategy"),
                       queries_count=len(research_plan.get("search_queries", [])))
            
            return state
            
        except Exception as e:
            logger.error("Error in research planning", error=str(e))
            state["research_plan"] = {"error": str(e)}
            return state
    
    async def search_web_node(state: ResearchState) -> ResearchState:
        """Execute web searches"""
        logger.info("Executing web search node", thread_id=state.get("thread_id"))
        
        try:
            search_results = await researcher.search_web(
                research_plan=state["research_plan"],
                query_analysis=state["query_analysis"]
            )
            
            state["search_results"] = search_results
            state["nodes_executed"] = state.get("nodes_executed", []) + ["search_web"]
            
            # Update thinking trace
            thinking_trace = state.get("thinking_trace", {})
            thinking_trace["web_search"] = {
                "total_results": len(search_results),
                "sources": [r.get("url") for r in search_results[:5]],  # First 5 URLs
                "timestamp": datetime.now().isoformat(),
            }
            state["thinking_trace"] = thinking_trace
            
            logger.info("Web search completed",
                       results_count=len(search_results))
            
            return state
            
        except Exception as e:
            logger.error("Error in web search", error=str(e))
            state["search_results"] = []
            return state
    
    async def scrape_content_node(state: ResearchState) -> ResearchState:
        """Scrape content from search results"""
        logger.info("Executing content scraping node", thread_id=state.get("thread_id"))
        
        try:
            scraped_content = await researcher.scrape_content(
                search_results=state["search_results"],
                query_analysis=state["query_analysis"]
            )
            
            state["scraped_content"] = scraped_content
            state["nodes_executed"] = state.get("nodes_executed", []) + ["scrape_content"]
            
            # Update thinking trace
            thinking_trace = state.get("thinking_trace", {})
            thinking_trace["content_scraping"] = {
                "pages_scraped": len(scraped_content),
                "total_content_length": sum(len(c.get("content", "")) for c in scraped_content),
                "timestamp": datetime.now().isoformat(),
            }
            state["thinking_trace"] = thinking_trace
            
            logger.info("Content scraping completed",
                       pages_scraped=len(scraped_content))
            
            return state
            
        except Exception as e:
            logger.error("Error in content scraping", error=str(e))
            state["scraped_content"] = []
            return state
    
    async def deduplicate_sources_node(state: ResearchState) -> ResearchState:
        """Deduplicate and rank sources"""
        logger.info("Executing source deduplication node", thread_id=state.get("thread_id"))
        
        try:
            deduplicated_sources = await researcher.deduplicate_sources(
                scraped_content=state["scraped_content"],
                max_sources=10  # Configurable
            )
            
            state["deduplicated_sources"] = deduplicated_sources
            state["nodes_executed"] = state.get("nodes_executed", []) + ["deduplicate_sources"]
            
            # Update thinking trace
            thinking_trace = state.get("thinking_trace", {})
            thinking_trace["deduplication"] = {
                "original_count": len(state["scraped_content"]),
                "deduplicated_count": len(deduplicated_sources),
                "timestamp": datetime.now().isoformat(),
            }
            state["thinking_trace"] = thinking_trace
            
            logger.info("Source deduplication completed",
                       original_count=len(state["scraped_content"]),
                       final_count=len(deduplicated_sources))
            
            return state
            
        except Exception as e:
            logger.error("Error in source deduplication", error=str(e))
            state["deduplicated_sources"] = state["scraped_content"]
            return state
    
    async def analyze_data_node(state: ResearchState) -> ResearchState:
        """Analyze the collected data"""
        logger.info("Executing data analysis node", thread_id=state.get("thread_id"))
        
        try:
            analysis_results = await analyzer.analyze_financial_data(
                query_analysis=state["query_analysis"],
                sources=state["deduplicated_sources"],
                conversation_history=state.get("conversation_history", [])
            )
            
            state["analysis_results"] = analysis_results
            state["nodes_executed"] = state.get("nodes_executed", []) + ["analyze_data"]
            
            # Update thinking trace
            thinking_trace = state.get("thinking_trace", {})
            thinking_trace["analysis"] = {
                "key_insights": analysis_results.get("key_insights", [])[:3],  # Top 3
                "data_points": len(analysis_results.get("data_points", [])),
                "confidence_score": analysis_results.get("confidence_score"),
                "timestamp": datetime.now().isoformat(),
            }
            state["thinking_trace"] = thinking_trace
            
            logger.info("Data analysis completed",
                       insights_count=len(analysis_results.get("key_insights", [])))
            
            return state
            
        except Exception as e:
            logger.error("Error in data analysis", error=str(e))
            state["analysis_results"] = {"error": str(e)}
            return state
    
    async def synthesize_response_node(state: ResearchState) -> ResearchState:
        """Synthesize the final response"""
        logger.info("Executing response synthesis node", thread_id=state.get("thread_id"))
        
        try:
            synthesis_result = await synthesizer.synthesize_response(
                query=state["query"],
                query_analysis=state["query_analysis"],
                analysis_results=state["analysis_results"],
                sources=state["deduplicated_sources"],
                conversation_history=state.get("conversation_history", [])
            )
            
            state["final_response"] = synthesis_result["response"]
            state["sources"] = synthesis_result["sources"]
            state["nodes_executed"] = state.get("nodes_executed", []) + ["synthesize_response"]
            
            # Update thinking trace
            thinking_trace = state.get("thinking_trace", {})
            thinking_trace["synthesis"] = {
                "response_length": len(synthesis_result["response"]),
                "sources_cited": len(synthesis_result["sources"]),
                "timestamp": datetime.now().isoformat(),
            }
            state["thinking_trace"] = thinking_trace
            
            logger.info("Response synthesis completed",
                       response_length=len(synthesis_result["response"]),
                       sources_cited=len(synthesis_result["sources"]))
            
            return state
            
        except Exception as e:
            logger.error("Error in response synthesis", error=str(e))
            state["final_response"] = f"I apologize, but I encountered an error while synthesizing the response: {str(e)}"
            state["sources"] = []
            return state
    
    async def update_memory_node(state: ResearchState) -> ResearchState:
        """Update memory with learnings"""
        logger.info("Executing memory update node", thread_id=state.get("thread_id"))
        
        try:
            # Update short-term memory (conversation context)
            await short_term_memory.store_conversation(
                thread_id=state["thread_id"],
                user_id=state["user_id"],
                query=state["query"],
                response=state["final_response"],
                sources=state["sources"],
                analysis=state["analysis_results"]
            )
            
            # Update long-term memory (insights and facts)
            if state["analysis_results"].get("key_insights"):
                await long_term_memory.store_insights(
                    user_id=state["user_id"],
                    thread_id=state["thread_id"],
                    insights=state["analysis_results"]["key_insights"],
                    entities=state["query_analysis"].get("entities", [])
                )
            
            state["nodes_executed"] = state.get("nodes_executed", []) + ["update_memory"]
            
            logger.info("Memory update completed", thread_id=state["thread_id"])
            
            return state
            
        except Exception as e:
            logger.error("Error in memory update", error=str(e))
            return state
    
    # Create the workflow graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("analyze_query", analyze_query_node)
    workflow.add_node("plan_research", plan_research_node)
    workflow.add_node("search_web", search_web_node)
    workflow.add_node("scrape_content", scrape_content_node)
    workflow.add_node("deduplicate_sources", deduplicate_sources_node)
    workflow.add_node("analyze_data", analyze_data_node)
    workflow.add_node("synthesize_response", synthesize_response_node)
    workflow.add_node("update_memory", update_memory_node)
    
    # Add edges
    workflow.add_edge(START, "analyze_query")
    workflow.add_edge("analyze_query", "plan_research")
    workflow.add_edge("plan_research", "search_web")
    workflow.add_edge("search_web", "scrape_content")
    workflow.add_edge("scrape_content", "deduplicate_sources")
    workflow.add_edge("deduplicate_sources", "analyze_data")
    workflow.add_edge("analyze_data", "synthesize_response")
    workflow.add_edge("synthesize_response", "update_memory")
    workflow.add_edge("update_memory", END)
    
    # Set entry point
    workflow.set_entry_point("analyze_query")
    
    # Add memory for checkpointing
    memory = MemorySaver()
    
    # Compile the graph
    graph = workflow.compile(checkpointer=memory)
    
    return graph