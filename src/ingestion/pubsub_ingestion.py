"""
Data Ingestion Module for ChainSight AI.
Generates synthetic supply chain news and publishes to Google Cloud Pub/Sub.
"""
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.cloud import pubsub_v1
from config import config


class NewsGenerator:
    """Generate synthetic supply chain news events."""
    
    COMPANIES = [
        "GlobalTech Corp", "TransWorld Logistics", "Pacific Manufacturing",
        "EuroSupply Chain", "AsiaLink Industries", "NorthStar Shipping",
        "MegaFactory Inc", "Continental Freight", "OceanWide Transport"
    ]
    
    LOCATIONS = [
        "Shanghai, China", "Rotterdam, Netherlands", "Los Angeles, USA",
        "Singapore", "Hamburg, Germany", "Hong Kong", "Dubai, UAE",
        "Tokyo, Japan", "Mumbai, India", "Sao Paulo, Brazil"
    ]
    
    DISRUPTION_TYPES = {
        "financial": [
            "bankruptcy filing", "credit rating downgrade", "debt restructuring",
            "liquidity crisis", "loan default", "payment delays"
        ],
        "labor": [
            "strike action", "labor shortage", "union negotiations",
            "wage disputes", "safety protests", "work stoppage"
        ],
        "operational": [
            "equipment failure", "capacity constraints", "quality issues",
            "production delays", "facility closure", "system outage"
        ],
        "environmental": [
            "severe weather", "natural disaster", "port congestion",
            "route disruption", "supply shortage", "demand surge"
        ]
    }
    
    SENTIMENT_TEMPLATES = {
        "negative": [
            "{company} faces {disruption} in {location}, causing significant supply chain delays.",
            "Major disruption: {company} reports {disruption} affecting operations in {location}.",
            "Supply chain alert: {disruption} at {company}'s {location} facility raises concerns.",
            "{company} struggles with {disruption} in {location}, impacting delivery schedules."
        ],
        "neutral": [
            "{company} announces {disruption} in {location}, monitoring situation closely.",
            "Update: {company} experiencing {disruption} in {location}, assessing impact.",
            "{company} reports {disruption} incident in {location}, implementing contingency plans."
        ],
        "positive": [
            "{company} successfully resolves {disruption} in {location}, operations resuming.",
            "{company} mitigates {disruption} risk in {location} with proactive measures.",
            "Recovery: {company} overcomes {disruption} challenges in {location}."
        ]
    }
    
    def generate_event(self) -> Dict:
        """Generate a single synthetic news event."""
        company = random.choice(self.COMPANIES)
        location = random.choice(self.LOCATIONS)
        disruption_category = random.choice(list(self.DISRUPTION_TYPES.keys()))
        disruption = random.choice(self.DISRUPTION_TYPES[disruption_category])
        sentiment = random.choice(["negative", "neutral", "positive"])
        
        # Bias towards negative sentiment for realistic risk scenarios
        if random.random() < 0.6:
            sentiment = "negative"
        
        template = random.choice(self.SENTIMENT_TEMPLATES[sentiment])
        headline = template.format(
            company=company,
            disruption=disruption,
            location=location
        )
        
        return {
            "event_id": f"evt_{datetime.now().timestamp()}_{random.randint(1000, 9999)}",
            "timestamp": datetime.now().isoformat(),
            "headline": headline,
            "company": company,
            "location": location,
            "disruption_type": disruption_category,
            "disruption": disruption,
            "expected_sentiment": sentiment,  # For validation
            "severity": random.choice(["low", "medium", "high"]),
            "impact_area": random.choice(["logistics", "manufacturing", "distribution", "procurement"])
        }


class PubSubPublisher:
    """Publish news events to Google Cloud Pub/Sub."""
    
    def __init__(self, project_id: Optional[str] = None, topic_name: Optional[str] = None):
        """Initialize Pub/Sub publisher."""
        self.project_id = project_id or config.gcp.project_id
        self.topic_name = topic_name or config.gcp.pubsub_topic
        
        if not self.project_id:
            raise ValueError("GCP Project ID is required")
        
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
    
    def publish(self, event: Dict) -> str:
        """Publish a single event to Pub/Sub."""
        data = json.dumps(event).encode("utf-8")
        future = self.publisher.publish(self.topic_path, data)
        return future.result()
    
    def publish_batch(self, events: List[Dict]) -> List[str]:
        """Publish multiple events to Pub/Sub."""
        message_ids = []
        for event in events:
            message_id = self.publish(event)
            message_ids.append(message_id)
        return message_ids
    
    def create_topic_if_not_exists(self) -> None:
        """Create the Pub/Sub topic if it doesn't exist."""
        try:
            self.publisher.create_topic(request={"name": self.topic_path})
            print(f"Created topic: {self.topic_path}")
        except Exception as e:
            if "ALREADY_EXISTS" in str(e):
                print(f"Topic already exists: {self.topic_path}")
            else:
                raise


class DataIngestionPipeline:
    """Main data ingestion pipeline."""
    
    def __init__(self):
        """Initialize the ingestion pipeline."""
        self.generator = NewsGenerator()
        self.publisher = None
    
    def setup_pubsub(self) -> None:
        """Setup Pub/Sub publisher and create topic."""
        try:
            self.publisher = PubSubPublisher()
            self.publisher.create_topic_if_not_exists()
            print("Pub/Sub setup completed")
        except Exception as e:
            print(f"Pub/Sub setup skipped (likely running in local/demo mode): {e}")
    
    def generate_and_publish(self, count: int = 10) -> List[Dict]:
        """Generate and publish synthetic news events."""
        events = [self.generator.generate_event() for _ in range(count)]
        
        if self.publisher:
            try:
                message_ids = self.publisher.publish_batch(events)
                print(f"Published {len(message_ids)} events to Pub/Sub")
            except Exception as e:
                print(f"Failed to publish to Pub/Sub: {e}")
                print("Events generated but not published")
        else:
            print(f"Generated {len(events)} events (Pub/Sub not configured)")
        
        return events
    
    def run_continuous(self, interval_seconds: int = 5, batch_size: int = 5) -> None:
        """Run continuous event generation."""
        import time
        
        print(f"Starting continuous ingestion (batch_size={batch_size}, interval={interval_seconds}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                events = self.generate_and_publish(count=batch_size)
                print(f"[{datetime.now().isoformat()}] Generated {len(events)} events")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nStopped continuous ingestion")


if __name__ == "__main__":
    # Demo mode - generate sample events
    pipeline = DataIngestionPipeline()
    events = pipeline.generate_and_publish(count=5)
    
    print("\nSample Events:")
    for event in events[:3]:
        print(f"\n{event['headline']}")
        print(f"  Category: {event['disruption_type']}, Sentiment: {event['expected_sentiment']}")
