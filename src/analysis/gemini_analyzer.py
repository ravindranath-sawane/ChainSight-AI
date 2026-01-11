"""
Analysis Module for ChainSight AI.
Uses Google Gemini Pro for entity extraction and sentiment analysis.
"""
import json
import re
from typing import Dict, List, Optional
import google.generativeai as genai
from config import config


class GeminiAnalyzer:
    """Analyze supply chain news using Gemini Pro."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize Gemini analyzer."""
        self.api_key = api_key or config.gcp.gemini_api_key
        self.model_name = model_name or config.gcp.gemini_model
        
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def analyze_news_event(self, event: Dict) -> Dict:
        """
        Analyze a single news event using Gemini.
        Extracts entities, sentiment, and risk assessment.
        """
        headline = event.get("headline", "")
        location = event.get("location", "")
        company = event.get("company", "")
        
        prompt = f"""Analyze this supply chain news event and provide structured insights:

Headline: {headline}
Company: {company}
Location: {location}

Please provide:
1. Entities: List key entities (companies, locations, products, services)
2. Sentiment: Classify as POSITIVE, NEUTRAL, or NEGATIVE
3. Sentiment Score: Rate from -1.0 (very negative) to +1.0 (very positive)
4. Risk Level: Classify as LOW, MEDIUM, or HIGH
5. Key Impacts: List 2-3 specific supply chain impacts
6. Summary: Brief analysis (1-2 sentences)

Respond in JSON format:
{{
    "entities": ["entity1", "entity2", ...],
    "sentiment": "POSITIVE|NEUTRAL|NEGATIVE",
    "sentiment_score": 0.5,
    "risk_level": "LOW|MEDIUM|HIGH",
    "key_impacts": ["impact1", "impact2"],
    "analysis_summary": "Brief summary here"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            analysis = self._parse_response(response.text)
            
            # Combine original event with analysis
            result = event.copy()
            result.update({
                "entities": json.dumps(analysis.get("entities", [])),
                "sentiment": analysis.get("sentiment", "NEUTRAL"),
                "sentiment_score": analysis.get("sentiment_score", 0.0),
                "risk_level": analysis.get("risk_level", "MEDIUM"),
                "key_impacts": json.dumps(analysis.get("key_impacts", [])),
                "analysis_summary": analysis.get("analysis_summary", "")
            })
            
            return result
            
        except Exception as e:
            print(f"Error analyzing event {event.get('event_id')}: {e}")
            # Return event with default analysis on error
            return self._get_fallback_analysis(event)
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response text to extract JSON."""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # If no JSON found, parse manually
                return self._manual_parse(response_text)
        except json.JSONDecodeError:
            return self._manual_parse(response_text)
    
    def _manual_parse(self, text: str) -> Dict:
        """Manually parse response if JSON parsing fails."""
        result = {
            "entities": [],
            "sentiment": "NEUTRAL",
            "sentiment_score": 0.0,
            "risk_level": "MEDIUM",
            "key_impacts": [],
            "analysis_summary": text[:200] if text else "Analysis unavailable"
        }
        
        # Try to extract sentiment
        if "NEGATIVE" in text.upper():
            result["sentiment"] = "NEGATIVE"
            result["sentiment_score"] = -0.5
        elif "POSITIVE" in text.upper():
            result["sentiment"] = "POSITIVE"
            result["sentiment_score"] = 0.5
        
        # Try to extract risk level
        if "HIGH" in text.upper() and "RISK" in text.upper():
            result["risk_level"] = "HIGH"
        elif "LOW" in text.upper() and "RISK" in text.upper():
            result["risk_level"] = "LOW"
        
        return result
    
    def _get_fallback_analysis(self, event: Dict) -> Dict:
        """Provide fallback analysis based on event metadata."""
        result = event.copy()
        
        # Use expected_sentiment if available
        sentiment_map = {
            "positive": ("POSITIVE", 0.5),
            "neutral": ("NEUTRAL", 0.0),
            "negative": ("NEGATIVE", -0.5)
        }
        
        expected_sentiment = event.get("expected_sentiment", "neutral")
        sentiment, score = sentiment_map.get(expected_sentiment, ("NEUTRAL", 0.0))
        
        # Map severity to risk level
        severity_to_risk = {
            "low": "LOW",
            "medium": "MEDIUM",
            "high": "HIGH"
        }
        risk_level = severity_to_risk.get(event.get("severity", "medium"), "MEDIUM")
        
        result.update({
            "entities": json.dumps([event.get("company", ""), event.get("location", "")]),
            "sentiment": sentiment,
            "sentiment_score": score,
            "risk_level": risk_level,
            "key_impacts": json.dumps([
                f"{event.get('disruption_type', 'operational')} disruption",
                f"Impact on {event.get('impact_area', 'operations')}"
            ]),
            "analysis_summary": f"Fallback analysis for {event.get('disruption_type')} event"
        })
        
        return result
    
    def analyze_batch(self, events: List[Dict], max_workers: int = 5) -> List[Dict]:
        """Analyze multiple events (sequentially or in parallel)."""
        analyzed_events = []
        
        for i, event in enumerate(events):
            print(f"Analyzing event {i+1}/{len(events)}: {event.get('event_id')}")
            analyzed_event = self.analyze_news_event(event)
            analyzed_events.append(analyzed_event)
        
        return analyzed_events


class RiskAggregator:
    """Aggregate and summarize risk across multiple events."""
    
    @staticmethod
    def aggregate_risks(analyzed_events: List[Dict]) -> Dict:
        """Aggregate risk metrics from analyzed events."""
        if not analyzed_events:
            return {
                "total_events": 0,
                "risk_distribution": {},
                "sentiment_distribution": {},
                "avg_sentiment_score": 0.0,
                "top_entities": [],
                "top_locations": []
            }
        
        risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        sentiment_scores = []
        entities = []
        locations = []
        
        for event in analyzed_events:
            # Count risk levels
            risk_level = event.get("risk_level", "MEDIUM")
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            # Count sentiments
            sentiment = event.get("sentiment", "NEUTRAL")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            # Collect sentiment scores
            if "sentiment_score" in event:
                sentiment_scores.append(event["sentiment_score"])
            
            # Collect entities
            if "entities" in event:
                if isinstance(event["entities"], str):
                    try:
                        event_entities = json.loads(event["entities"])
                        entities.extend(event_entities)
                    except:
                        pass
                else:
                    entities.extend(event["entities"])
            
            # Collect locations
            if "location" in event:
                locations.append(event["location"])
        
        # Calculate top entities and locations
        from collections import Counter
        entity_counts = Counter(entities)
        location_counts = Counter(locations)
        
        return {
            "total_events": len(analyzed_events),
            "risk_distribution": risk_counts,
            "sentiment_distribution": sentiment_counts,
            "avg_sentiment_score": sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0,
            "top_entities": [{"entity": e, "count": c} for e, c in entity_counts.most_common(10)],
            "top_locations": [{"location": l, "count": c} for l, c in location_counts.most_common(10)]
        }


if __name__ == "__main__":
    # Demo mode with sample event
    sample_event = {
        "event_id": "test_001",
        "timestamp": "2024-01-01T00:00:00",
        "headline": "GlobalTech Corp faces strike action in Shanghai, China, causing significant supply chain delays.",
        "company": "GlobalTech Corp",
        "location": "Shanghai, China",
        "disruption_type": "labor",
        "expected_sentiment": "negative",
        "severity": "high"
    }
    
    print("Sample Event:")
    print(json.dumps(sample_event, indent=2))
    print("\nNote: Gemini analysis requires valid API key")
