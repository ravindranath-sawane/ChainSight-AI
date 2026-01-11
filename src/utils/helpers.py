"""Utility functions for ChainSight AI."""

import json
from typing import Dict, Any


def format_event_for_display(event: Dict[str, Any]) -> str:
    """Format an event for human-readable display."""
    lines = [
        f"Event ID: {event.get('event_id', 'N/A')}",
        f"Timestamp: {event.get('timestamp', 'N/A')}",
        f"Headline: {event.get('headline', 'N/A')}",
        f"Company: {event.get('company', 'N/A')}",
        f"Location: {event.get('location', 'N/A')}",
        f"Risk Level: {event.get('risk_level', 'N/A')}",
        f"Sentiment: {event.get('sentiment', 'N/A')} ({event.get('sentiment_score', 0):.2f})",
    ]
    return "\n".join(lines)


def parse_json_field(field_value: Any) -> Any:
    """Parse JSON string field if needed."""
    if isinstance(field_value, str):
        try:
            return json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            return field_value
    return field_value


def validate_event_schema(event: Dict[str, Any]) -> bool:
    """Validate that an event has required fields."""
    required_fields = ['event_id', 'timestamp', 'headline']
    return all(field in event for field in required_fields)


def calculate_risk_score(event: Dict[str, Any]) -> float:
    """Calculate a numeric risk score from event attributes."""
    risk_level_scores = {
        'LOW': 0.3,
        'MEDIUM': 0.6,
        'HIGH': 0.9
    }
    
    sentiment_weight = 0.7
    risk_weight = 0.3
    
    sentiment_score = event.get('sentiment_score', 0.0)
    risk_level = event.get('risk_level', 'MEDIUM')
    risk_score = risk_level_scores.get(risk_level, 0.5)
    
    # Negative sentiment increases risk
    adjusted_sentiment = -sentiment_score if sentiment_score < 0 else 0
    
    final_score = (risk_score * risk_weight) + (adjusted_sentiment * sentiment_weight)
    return max(0.0, min(1.0, final_score))
