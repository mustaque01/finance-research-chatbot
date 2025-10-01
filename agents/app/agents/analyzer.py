"""
Analyzer Agent - Handles financial data analysis and insights generation
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import re
import json

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class AnalyzerAgent:
    """Agent responsible for analyzing financial data and generating insights"""
    
    def __init__(self):
        self.financial_metrics = {
            "valuation": ["P/E", "P/B", "EV/EBITDA", "PEG", "price to sales"],
            "profitability": ["ROE", "ROA", "profit margin", "operating margin", "EBITDA margin"],
            "liquidity": ["current ratio", "quick ratio", "cash ratio", "working capital"],
            "leverage": ["debt to equity", "debt ratio", "interest coverage", "EBITDA to interest"],
            "efficiency": ["asset turnover", "inventory turnover", "receivables turnover"],
            "growth": ["revenue growth", "earnings growth", "dividend growth", "book value growth"]
        }
    
    async def analyze_financial_data(
        self,
        query_analysis: Dict[str, Any],
        sources: List[Dict[str, Any]],
        conversation_history: List[Any] = None
    ) -> Dict[str, Any]:
        """Analyze financial data from sources and generate insights"""
        
        logger.info("Starting financial data analysis", 
                   sources_count=len(sources),
                   query_intent=query_analysis.get("intent"))
        
        try:
            # Extract relevant entities and context
            entities = query_analysis.get("entities", [])
            intent = query_analysis.get("intent", "general_inquiry")
            
            # Analyze content from sources
            key_insights = []
            data_points = []
            financial_metrics = {}
            trends = []
            risk_factors = []
            
            # Process each source
            for source in sources:
                content = source.get("content", "")
                if not content:
                    continue
                
                # Extract financial metrics
                metrics = await self._extract_financial_metrics(content, entities)
                if metrics:
                    financial_metrics.update(metrics)
                
                # Extract key insights
                insights = await self._extract_insights(content, intent)
                key_insights.extend(insights)
                
                # Extract data points
                data = await self._extract_data_points(content)
                data_points.extend(data)
                
                # Identify trends
                trend_data = await self._identify_trends(content)
                trends.extend(trend_data)
                
                # Identify risk factors
                risks = await self._identify_risks(content)
                risk_factors.extend(risks)
            
            # Generate analysis summary
            analysis_summary = await self._generate_analysis_summary(
                query_analysis, key_insights, financial_metrics, trends, risk_factors
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                len(sources), len(key_insights), len(data_points)
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                intent, financial_metrics, trends, risk_factors
            )
            
            result = {
                "analysis_summary": analysis_summary,
                "key_insights": key_insights[:10],  # Top 10 insights
                "financial_metrics": financial_metrics,
                "data_points": data_points[:20],  # Top 20 data points
                "trends": trends[:5],  # Top 5 trends
                "risk_factors": risk_factors[:5],  # Top 5 risks
                "recommendations": recommendations,
                "confidence_score": confidence_score,
                "sources_analyzed": len(sources),
                "timestamp": datetime.now().isoformat(),
            }
            
            logger.info("Financial analysis completed",
                       insights_count=len(key_insights),
                       metrics_count=len(financial_metrics),
                       confidence=confidence_score)
            
            return result
            
        except Exception as e:
            logger.error("Error in financial data analysis", error=str(e))
            return {
                "error": f"Analysis failed: {str(e)}",
                "analysis_summary": "Unable to complete analysis due to technical issues.",
                "key_insights": [],
                "financial_metrics": {},
                "data_points": [],
                "trends": [],
                "risk_factors": [],
                "recommendations": [],
                "confidence_score": 0.0,
                "sources_analyzed": len(sources),
                "timestamp": datetime.now().isoformat(),
            }
    
    async def _extract_financial_metrics(
        self, 
        content: str, 
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract financial metrics from content"""
        
        metrics = {}
        content_lower = content.lower()
        
        # Look for specific metric patterns
        metric_patterns = {
            "pe_ratio": r"p/e\s*ratio?\s*(?:of\s*)?(\d+\.?\d*)",
            "price_to_book": r"p/b\s*ratio?\s*(?:of\s*)?(\d+\.?\d*)",
            "debt_to_equity": r"debt.to.equity\s*ratio?\s*(?:of\s*)?(\d+\.?\d*)",
            "roe": r"(?:return\s*on\s*equity|roe)\s*(?:of\s*)?(\d+\.?\d*)%?",
            "revenue_growth": r"revenue\s*growth\s*(?:of\s*)?(\d+\.?\d*)%",
            "profit_margin": r"profit\s*margin\s*(?:of\s*)?(\d+\.?\d*)%",
        }
        
        for metric_name, pattern in metric_patterns.items():
            matches = re.findall(pattern, content_lower)
            if matches:
                try:
                    value = float(matches[0])
                    metrics[metric_name] = value
                except ValueError:
                    continue
        
        # Look for percentage values
        percentage_matches = re.findall(r"(\d+\.?\d*)%", content)
        if percentage_matches:
            metrics["percentage_values"] = [float(x) for x in percentage_matches[:5]]
        
        # Look for currency amounts
        currency_pattern = r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:billion|million|thousand)?"
        currency_matches = re.findall(currency_pattern, content)
        if currency_matches:
            metrics["currency_amounts"] = currency_matches[:5]
        
        return metrics
    
    async def _extract_insights(self, content: str, intent: str) -> List[str]:
        """Extract key insights from content"""
        
        insights = []
        sentences = content.split('. ')
        
        # Keywords that indicate important insights
        insight_keywords = [
            "significant", "important", "notable", "remarkable", "strong",
            "weak", "improved", "declined", "increased", "decreased",
            "outperformed", "underperformed", "growth", "decline",
            "profit", "loss", "revenue", "earnings", "forecast"
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 200:
                continue
            
            # Check if sentence contains insight keywords
            if any(keyword in sentence.lower() for keyword in insight_keywords):
                insights.append(sentence)
                
                if len(insights) >= 15:  # Limit insights
                    break
        
        return insights
    
    async def _extract_data_points(self, content: str) -> List[Dict[str, Any]]:
        """Extract structured data points from content"""
        
        data_points = []
        
        # Number patterns with context
        number_pattern = r"(\w+(?:\s+\w+){0,3})\s+(?:is|was|of|at)\s+(\d+(?:,\d{3})*(?:\.\d+)?)\s*(\w+)?"
        matches = re.findall(number_pattern, content)
        
        for match in matches:
            context, value, unit = match
            try:
                numeric_value = float(value.replace(',', ''))
                data_points.append({
                    "context": context.strip(),
                    "value": numeric_value,
                    "unit": unit.strip() if unit else "",
                    "raw_text": f"{context} {value} {unit}".strip()
                })
            except ValueError:
                continue
        
        return data_points[:20]
    
    async def _identify_trends(self, content: str) -> List[Dict[str, Any]]:
        """Identify trends from content"""
        
        trends = []
        content_lower = content.lower()
        
        # Trend indicators
        positive_trends = ["increased", "grew", "rose", "improved", "gained", "up"]
        negative_trends = ["decreased", "fell", "declined", "dropped", "lost", "down"]
        
        sentences = content.split('. ')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            trend_type = None
            if any(word in sentence_lower for word in positive_trends):
                trend_type = "positive"
            elif any(word in sentence_lower for word in negative_trends):
                trend_type = "negative"
            
            if trend_type and len(sentence) > 30:
                trends.append({
                    "type": trend_type,
                    "description": sentence.strip(),
                    "strength": "moderate"  # Could be enhanced with sentiment analysis
                })
                
                if len(trends) >= 10:
                    break
        
        return trends
    
    async def _identify_risks(self, content: str) -> List[str]:
        """Identify risk factors from content"""
        
        risks = []
        risk_keywords = [
            "risk", "concern", "challenge", "threat", "uncertainty",
            "volatility", "decline", "loss", "debt", "liability"
        ]
        
        sentences = content.split('. ')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            if any(keyword in sentence_lower for keyword in risk_keywords):
                if len(sentence) > 20 and len(sentence) < 200:
                    risks.append(sentence.strip())
                    
                    if len(risks) >= 10:
                        break
        
        return risks
    
    async def _generate_analysis_summary(
        self,
        query_analysis: Dict[str, Any],
        insights: List[str],
        metrics: Dict[str, Any],
        trends: List[Dict[str, Any]],
        risks: List[str]
    ) -> str:
        """Generate a comprehensive analysis summary"""
        
        intent = query_analysis.get("intent", "general_inquiry")
        entities = query_analysis.get("entities", [])
        
        summary_parts = []
        
        # Add context about what was analyzed
        if entities:
            company_names = [e["value"] for e in entities if e["type"] == "company"]
            if company_names:
                summary_parts.append(f"Analysis of {', '.join(company_names[:3])}")
        
        # Add key findings
        if insights:
            summary_parts.append(f"Key findings from {len(insights)} insights analyzed")
        
        # Add metrics summary
        if metrics:
            summary_parts.append(f"Financial metrics evaluated: {len(metrics)} indicators")
        
        # Add trend analysis
        positive_trends = [t for t in trends if t.get("type") == "positive"]
        negative_trends = [t for t in trends if t.get("type") == "negative"]
        
        if positive_trends:
            summary_parts.append(f"{len(positive_trends)} positive trends identified")
        if negative_trends:
            summary_parts.append(f"{len(negative_trends)} negative trends identified")
        
        # Add risk assessment
        if risks:
            summary_parts.append(f"{len(risks)} risk factors noted")
        
        return ". ".join(summary_parts) + "."
    
    def _calculate_confidence_score(
        self, 
        sources_count: int, 
        insights_count: int, 
        data_points_count: int
    ) -> float:
        """Calculate confidence score for the analysis"""
        
        # Base score
        score = 0.0
        
        # Source quality factor
        if sources_count >= 5:
            score += 0.4
        elif sources_count >= 3:
            score += 0.3
        elif sources_count >= 1:
            score += 0.2
        
        # Insights factor
        if insights_count >= 10:
            score += 0.3
        elif insights_count >= 5:
            score += 0.2
        elif insights_count >= 1:
            score += 0.1
        
        # Data points factor
        if data_points_count >= 15:
            score += 0.3
        elif data_points_count >= 5:
            score += 0.2
        elif data_points_count >= 1:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _generate_recommendations(
        self,
        intent: str,
        metrics: Dict[str, Any],
        trends: List[Dict[str, Any]],
        risks: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Intent-based recommendations
        if intent == "investment":
            recommendations.append("Consider diversification to reduce risk exposure")
            recommendations.append("Monitor key financial ratios for valuation insights")
        elif intent == "analysis":
            recommendations.append("Focus on trend analysis for future projections")
            recommendations.append("Compare metrics with industry benchmarks")
        
        # Trend-based recommendations
        positive_trends = [t for t in trends if t.get("type") == "positive"]
        negative_trends = [t for t in trends if t.get("type") == "negative"]
        
        if len(positive_trends) > len(negative_trends):
            recommendations.append("Positive momentum detected - consider maintaining current strategy")
        elif len(negative_trends) > len(positive_trends):
            recommendations.append("Negative trends identified - review risk management approach")
        
        # Risk-based recommendations
        if len(risks) > 3:
            recommendations.append("Multiple risk factors present - conduct detailed risk assessment")
        
        # Metrics-based recommendations
        if "debt_to_equity" in metrics and metrics["debt_to_equity"] > 1.0:
            recommendations.append("High leverage detected - monitor debt management closely")
        
        if not recommendations:
            recommendations.append("Continue monitoring financial performance and market conditions")
        
        return recommendations[:5]  # Top 5 recommendations