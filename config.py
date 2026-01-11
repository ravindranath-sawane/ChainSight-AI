"""
Configuration management for ChainSight AI.
Manages GCP project settings and API credentials.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class GCPConfig(BaseModel):
    """Google Cloud Platform configuration."""
    project_id: str = Field(default="", description="GCP Project ID")
    location: str = Field(default="us-central1", description="GCP region")
    
    # Pub/Sub Configuration
    pubsub_topic: str = Field(default="supply-chain-news", description="Pub/Sub topic name")
    pubsub_subscription: str = Field(default="supply-chain-news-sub", description="Pub/Sub subscription name")
    
    # BigQuery Configuration
    dataset_id: str = Field(default="supply_chain_data", description="BigQuery dataset ID")
    raw_table_id: str = Field(default="raw_news", description="Raw news table ID")
    analyzed_table_id: str = Field(default="analyzed_news", description="Analyzed news table ID")
    
    # Gemini Configuration
    gemini_model: str = Field(default="gemini-pro", description="Gemini model name")
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key")


class AppConfig:
    """Application configuration manager."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.gcp = GCPConfig(
            project_id=os.getenv("GCP_PROJECT_ID", ""),
            location=os.getenv("GCP_LOCATION", "us-central1"),
            pubsub_topic=os.getenv("PUBSUB_TOPIC", "supply-chain-news"),
            pubsub_subscription=os.getenv("PUBSUB_SUBSCRIPTION", "supply-chain-news-sub"),
            dataset_id=os.getenv("BQ_DATASET_ID", "supply_chain_data"),
            raw_table_id=os.getenv("BQ_RAW_TABLE_ID", "raw_news"),
            analyzed_table_id=os.getenv("BQ_ANALYZED_TABLE_ID", "analyzed_news"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-pro"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
        )
    
    @property
    def credentials_path(self) -> Optional[Path]:
        """Get GCP credentials file path."""
        creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        return Path(creds) if creds else None


# Global configuration instance
config = AppConfig()
