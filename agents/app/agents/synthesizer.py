"""
Synthesizer Agent - Handles response generation and synthesis
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import json

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class SynthesizerAgent:
    """Agent responsible for synthesizing final responses from analyzed data"""
    
    def __init__(self):
        self.response_templates = {
            "analysis": "Based on my analysis of {sources_count} sources, here are the key findings:",
            "comparison": "Comparing the available data, I found the following insights:",
            "valuation": "Based on the valuation metrics and market data:",
            "prediction": "Based on current trends and historical data:",
            "general_inquiry": "Here's what I found regarding your question:",
        }
    
    async def synthesize_response(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        analysis_results: Dict[str, Any],
        sources: List[Dict[str, Any]],
        conversation_history: List[Any] = None
    ) -> Dict[str, Any]:
        """Synthesize a comprehensive response from analysis results"""
        
        logger.info("Starting response synthesis",
                   query_length=len(query),
                   sources_count=len(sources),
                   analysis_available=bool(analysis_results))
        
        try:
            intent = query_analysis.get("intent", "general_inquiry")
            entities = query_analysis.get("entities", [])
            
            # Handle analysis errors
            if "error" in analysis_results:
                return await self._handle_analysis_error(query, analysis_results["error"], sources)
            
            # Build response components
            response_components = []
            
            # 1. Introduction/Context
            intro = await self._build_introduction(query, intent, entities, len(sources))
            if intro:
                response_components.append(intro)
            
            # 2. Key Insights
            insights_section = await self._build_insights_section(analysis_results)
            if insights_section:
                response_components.append(insights_section)
            
            # 3. Financial Metrics
            metrics_section = await self._build_metrics_section(analysis_results)
            if metrics_section:
                response_components.append(metrics_section)
            
            # 4. Trends Analysis
            trends_section = await self._build_trends_section(analysis_results)
            if trends_section:
                response_components.append(trends_section)
            
            # 5. Risk Assessment
            risks_section = await self._build_risks_section(analysis_results)
            if risks_section:
                response_components.append(risks_section)
            
            # 6. Recommendations
            recommendations_section = await self._build_recommendations_section(analysis_results)
            if recommendations_section:
                response_components.append(recommendations_section)
            
            # 7. Disclaimer
            disclaimer = await self._build_disclaimer(analysis_results.get("confidence_score", 0.0))
            if disclaimer:
                response_components.append(disclaimer)
            
            # Combine all components
            final_response = "\n\n".join(response_components)
            
            # Prepare source citations
            source_citations = await self._prepare_source_citations(sources)
            
            # Quality check
            quality_score = self._calculate_response_quality(
                final_response, analysis_results, len(sources)
            )
            
            result = {
                "response": final_response,
                "sources": source_citations,
                "quality_score": quality_score,
                "word_count": len(final_response.split()),
                "sections_included": len(response_components),
                "timestamp": datetime.now().isoformat(),
            }
            
            logger.info("Response synthesis completed",
                       response_length=len(final_response),
                       sources_cited=len(source_citations),
                       quality_score=quality_score)
            
            return result
            
        except Exception as e:
            logger.error("Error in response synthesis", error=str(e))
            return await self._handle_synthesis_error(query, str(e))
    
    async def _build_introduction(
        self, 
        query: str, 
        intent: str, 
        entities: List[Dict[str, Any]], 
        sources_count: int
    ) -> str:
        """Build the introduction section"""
        
        template = self.response_templates.get(intent, self.response_templates["general_inquiry"])
        intro = template.format(sources_count=sources_count)
        
        # Add entity context if available
        if entities:
            company_entities = [e["value"] for e in entities if e["type"] == "company"]
            if company_entities:
                companies_text = ", ".join(company_entities[:3])
                if len(company_entities) > 3:
                    companies_text += f" and {len(company_entities) - 3} others"
                intro += f" I've analyzed information about {companies_text}."
        
        return intro
    
    async def _build_insights_section(self, analysis_results: Dict[str, Any]) -> str:
        """Build the key insights section"""
        
        insights = analysis_results.get("key_insights", [])
        if not insights:
            return ""
        
        section = "## Key Insights\n"
        
        # Select top insights
        top_insights = insights[:5]
        for i, insight in enumerate(top_insights, 1):
            # Clean up the insight text
            clean_insight = insight.strip()
            if not clean_insight.endswith('.'):
                clean_insight += '.'
            section += f"{i}. {clean_insight}\n"
        
        return section
    
    async def _build_metrics_section(self, analysis_results: Dict[str, Any]) -> str:
        """Build the financial metrics section"""
        
        metrics = analysis_results.get("financial_metrics", {})
        if not metrics:
            return ""
        
        section = "## Financial Metrics\n"
        
        # Format different types of metrics
        formatted_metrics = []
        
        # Ratio metrics
        ratio_metrics = {
            "pe_ratio": "P/E Ratio",
            "price_to_book": "Price-to-Book Ratio",
            "debt_to_equity": "Debt-to-Equity Ratio",
            "roe": "Return on Equity",
        }
        
        for key, label in ratio_metrics.items():
            if key in metrics:
                value = metrics[key]
                if key == "roe":
                    formatted_metrics.append(f"• **{label}**: {value}%")
                else:
                    formatted_metrics.append(f"• **{label}**: {value}")
        
        # Growth metrics
        if "revenue_growth" in metrics:
            formatted_metrics.append(f"• **Revenue Growth**: {metrics['revenue_growth']}%")
        
        if "profit_margin" in metrics:
            formatted_metrics.append(f"• **Profit Margin**: {metrics['profit_margin']}%")
        
        # Currency amounts
        if "currency_amounts" in metrics:
            amounts = metrics["currency_amounts"][:3]
            for amount in amounts:
                formatted_metrics.append(f"• **Key Financial Figure**: ${amount}")
        
        if formatted_metrics:
            section += "\n".join(formatted_metrics)
            return section
        
        return ""
    
    async def _build_trends_section(self, analysis_results: Dict[str, Any]) -> str:
        """Build the trends analysis section"""
        
        trends = analysis_results.get("trends", [])
        if not trends:
            return ""
        
        section = "## Market Trends\n"
        
        # Separate positive and negative trends
        positive_trends = [t for t in trends if t.get("type") == "positive"]
        negative_trends = [t for t in trends if t.get("type") == "negative"]
        
        if positive_trends:
            section += "**Positive Trends:**\n"
            for trend in positive_trends[:3]:
                description = trend.get("description", "").strip()
                if description:
                    section += f"• {description}\n"
        
        if negative_trends:
            if positive_trends:
                section += "\n"
            section += "**Areas of Concern:**\n"
            for trend in negative_trends[:3]:
                description = trend.get("description", "").strip()
                if description:
                    section += f"• {description}\n"
        
        return section
    
    async def _build_risks_section(self, analysis_results: Dict[str, Any]) -> str:
        """Build the risk assessment section"""
        
        risks = analysis_results.get("risk_factors", [])
        if not risks:
            return ""
        
        section = "## Risk Assessment\n"
        
        top_risks = risks[:4]
        for i, risk in enumerate(top_risks, 1):
            clean_risk = risk.strip()
            if not clean_risk.endswith('.'):
                clean_risk += '.'
            section += f"{i}. {clean_risk}\n"
        
        return section
    
    async def _build_recommendations_section(self, analysis_results: Dict[str, Any]) -> str:
        """Build the recommendations section"""
        
        recommendations = analysis_results.get("recommendations", [])
        if not recommendations:
            return ""
        
        section = "## Recommendations\n"
        
        for i, rec in enumerate(recommendations, 1):
            clean_rec = rec.strip()
            if not clean_rec.endswith('.'):
                clean_rec += '.'
            section += f"{i}. {clean_rec}\n"
        
        return section
    
    async def _build_disclaimer(self, confidence_score: float) -> str:
        """Build appropriate disclaimer based on confidence"""
        
        base_disclaimer = "**Important Note**: This analysis is based on publicly available information and should not be considered as financial advice. "
        
        if confidence_score >= 0.8:
            return base_disclaimer + "The analysis has high confidence based on multiple reliable sources."
        elif confidence_score >= 0.6:
            return base_disclaimer + "The analysis has moderate confidence based on available sources."
        elif confidence_score >= 0.4:
            return base_disclaimer + "The analysis has limited confidence due to fewer available sources."
        else:
            return base_disclaimer + "The analysis has low confidence due to limited data availability. Please verify findings independently."
    
    async def _prepare_source_citations(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare source citations for the response"""
        
        citations = []
        
        for i, source in enumerate(sources[:10], 1):  # Limit to top 10 sources
            citation = {
                "id": i,
                "title": source.get("title", "Unknown Title"),
                "url": source.get("url", ""),
                "domain": source.get("domain", ""),
                "snippet": source.get("snippet", "")[:150] + "..." if source.get("snippet", "") else "",
            }
            citations.append(citation)
        
        return citations
    
    async def _handle_analysis_error(
        self, 
        query: str, 
        error_message: str, 
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle cases where analysis failed"""
        
        fallback_response = f"""I apologize, but I encountered some technical difficulties while analyzing the data for your query: "{query}"

Despite this issue, I was able to gather information from {len(sources)} sources. However, I cannot provide a detailed analysis at this time due to the following error: {error_message}

Please try rephrasing your question or try again later. If the problem persists, you may want to contact support."""
        
        return {
            "response": fallback_response,
            "sources": await self._prepare_source_citations(sources),
            "quality_score": 0.3,
            "word_count": len(fallback_response.split()),
            "sections_included": 1,
            "timestamp": datetime.now().isoformat(),
        }
    
    async def _handle_synthesis_error(self, query: str, error_message: str) -> Dict[str, Any]:
        """Handle synthesis errors"""
        
        error_response = f"""I apologize, but I encountered an error while preparing my response to your query: "{query}"

Error details: {error_message}

Please try asking your question again, or contact support if this issue continues."""
        
        return {
            "response": error_response,
            "sources": [],
            "quality_score": 0.1,
            "word_count": len(error_response.split()),
            "sections_included": 1,
            "timestamp": datetime.now().isoformat(),
        }
    
    def _calculate_response_quality(
        self, 
        response: str, 
        analysis_results: Dict[str, Any], 
        sources_count: int
    ) -> float:
        """Calculate quality score for the response"""
        
        quality = 0.0
        
        # Length factor (reasonable length responses are better)
        word_count = len(response.split())
        if 200 <= word_count <= 800:
            quality += 0.3
        elif 100 <= word_count < 200 or 800 < word_count <= 1200:
            quality += 0.2
        elif word_count >= 50:
            quality += 0.1
        
        # Analysis quality factor
        confidence_score = analysis_results.get("confidence_score", 0.0)
        quality += confidence_score * 0.4
        
        # Sources factor
        if sources_count >= 5:
            quality += 0.2
        elif sources_count >= 3:
            quality += 0.15
        elif sources_count >= 1:
            quality += 0.1
        
        # Content richness factor
        insights_count = len(analysis_results.get("key_insights", []))
        metrics_count = len(analysis_results.get("financial_metrics", {}))
        
        if insights_count >= 5 and metrics_count >= 3:
            quality += 0.1
        elif insights_count >= 3 or metrics_count >= 2:
            quality += 0.05
        
        return min(quality, 1.0)  # Cap at 1.0