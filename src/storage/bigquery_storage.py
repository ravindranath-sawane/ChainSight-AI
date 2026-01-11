"""
Storage Module for ChainSight AI.
Handles BigQuery integration for storing raw and analyzed news data.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from config import config


class BigQueryStorage:
    """Manage BigQuery storage for supply chain data."""
    
    def __init__(self, project_id: Optional[str] = None, dataset_id: Optional[str] = None):
        """Initialize BigQuery client."""
        self.project_id = project_id or config.gcp.project_id
        self.dataset_id = dataset_id or config.gcp.dataset_id
        
        if not self.project_id:
            raise ValueError("GCP Project ID is required")
        
        self.client = bigquery.Client(project=self.project_id)
        self.dataset_ref = f"{self.project_id}.{self.dataset_id}"
    
    def create_dataset_if_not_exists(self) -> None:
        """Create the BigQuery dataset if it doesn't exist."""
        try:
            self.client.get_dataset(self.dataset_ref)
            print(f"Dataset already exists: {self.dataset_ref}")
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = config.gcp.location
            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"Created dataset: {self.dataset_ref}")
    
    def create_raw_news_table(self) -> None:
        """Create table for raw news events."""
        table_id = f"{self.dataset_ref}.{config.gcp.raw_table_id}"
        
        schema = [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("headline", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("disruption_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("disruption", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("expected_sentiment", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("severity", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("impact_area", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        try:
            self.client.get_table(table_id)
            print(f"Table already exists: {table_id}")
        except NotFound:
            table = bigquery.Table(table_id, schema=schema)
            table = self.client.create_table(table)
            print(f"Created table: {table_id}")
    
    def create_analyzed_news_table(self) -> None:
        """Create table for analyzed news with Gemini insights."""
        table_id = f"{self.dataset_ref}.{config.gcp.analyzed_table_id}"
        
        schema = [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("headline", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("disruption_type", "STRING", mode="NULLABLE"),
            # Gemini Analysis Fields
            bigquery.SchemaField("entities", "STRING", mode="NULLABLE"),  # JSON string
            bigquery.SchemaField("sentiment", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("sentiment_score", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("risk_level", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("key_impacts", "STRING", mode="NULLABLE"),  # JSON string
            bigquery.SchemaField("analysis_summary", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("analyzed_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        try:
            self.client.get_table(table_id)
            print(f"Table already exists: {table_id}")
        except NotFound:
            table = bigquery.Table(table_id, schema=schema)
            table = self.client.create_table(table)
            print(f"Created table: {table_id}")
    
    def setup_schema(self) -> None:
        """Setup complete BigQuery schema."""
        self.create_dataset_if_not_exists()
        self.create_raw_news_table()
        self.create_analyzed_news_table()
        print("BigQuery schema setup completed")
    
    def insert_raw_events(self, events: List[Dict]) -> None:
        """Insert raw news events into BigQuery."""
        if not events:
            return
        
        table_id = f"{self.dataset_ref}.{config.gcp.raw_table_id}"
        
        # Add ingestion timestamp
        rows_to_insert = []
        for event in events:
            row = event.copy()
            row["ingested_at"] = datetime.now().isoformat()
            # Convert timestamp string to proper format
            if "timestamp" in row and isinstance(row["timestamp"], str):
                row["timestamp"] = row["timestamp"]
            rows_to_insert.append(row)
        
        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        
        if errors:
            print(f"Errors inserting rows: {errors}")
        else:
            print(f"Inserted {len(rows_to_insert)} raw events into BigQuery")
    
    def insert_analyzed_events(self, events: List[Dict]) -> None:
        """Insert analyzed news events into BigQuery."""
        if not events:
            return
        
        table_id = f"{self.dataset_ref}.{config.gcp.analyzed_table_id}"
        
        # Add analysis timestamp
        rows_to_insert = []
        for event in events:
            row = event.copy()
            row["analyzed_at"] = datetime.now().isoformat()
            # Ensure JSON fields are strings
            if "entities" in row and not isinstance(row["entities"], str):
                row["entities"] = json.dumps(row["entities"])
            if "key_impacts" in row and not isinstance(row["key_impacts"], str):
                row["key_impacts"] = json.dumps(row["key_impacts"])
            rows_to_insert.append(row)
        
        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        
        if errors:
            print(f"Errors inserting analyzed rows: {errors}")
        else:
            print(f"Inserted {len(rows_to_insert)} analyzed events into BigQuery")
    
    def query_recent_events(self, table_name: str = "raw_news", limit: int = 100) -> List[Dict]:
        """Query recent events from BigQuery."""
        query = f"""
            SELECT *
            FROM `{self.dataset_ref}.{table_name}`
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            events = []
            for row in results:
                event = dict(row.items())
                # Convert timestamps to ISO format
                if "timestamp" in event:
                    event["timestamp"] = event["timestamp"].isoformat()
                if "ingested_at" in event:
                    event["ingested_at"] = event["ingested_at"].isoformat()
                if "analyzed_at" in event:
                    event["analyzed_at"] = event["analyzed_at"].isoformat()
                events.append(event)
            
            return events
        except Exception as e:
            print(f"Error querying BigQuery: {e}")
            return []
    
    def get_risk_summary(self) -> Dict:
        """Get risk summary statistics from analyzed events."""
        query = f"""
            SELECT 
                risk_level,
                sentiment,
                COUNT(*) as count,
                AVG(sentiment_score) as avg_sentiment_score
            FROM `{self.dataset_ref}.{config.gcp.analyzed_table_id}`
            WHERE analyzed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
            GROUP BY risk_level, sentiment
            ORDER BY count DESC
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            summary = {
                "total_events": 0,
                "by_risk_level": {},
                "by_sentiment": {}
            }
            
            for row in results:
                summary["total_events"] += row.count
                
                risk_level = row.risk_level or "unknown"
                if risk_level not in summary["by_risk_level"]:
                    summary["by_risk_level"][risk_level] = 0
                summary["by_risk_level"][risk_level] += row.count
                
                sentiment = row.sentiment or "unknown"
                if sentiment not in summary["by_sentiment"]:
                    summary["by_sentiment"][sentiment] = 0
                summary["by_sentiment"][sentiment] += row.count
            
            return summary
        except Exception as e:
            print(f"Error getting risk summary: {e}")
            return {"total_events": 0, "by_risk_level": {}, "by_sentiment": {}}


if __name__ == "__main__":
    # Demo mode
    storage = BigQueryStorage()
    print("BigQuery Storage initialized")
    print(f"Dataset: {storage.dataset_ref}")
