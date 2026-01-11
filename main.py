"""
Main Pipeline for ChainSight AI.
Orchestrates the complete data flow: Ingest -> Store -> Analyze -> Visualize.
"""
import sys
import os
import argparse
from datetime import datetime
from typing import Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from config import config
from src.ingestion.pubsub_ingestion import DataIngestionPipeline
from src.storage.bigquery_storage import BigQueryStorage
from src.analysis.gemini_analyzer import GeminiAnalyzer


class ChainSightPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, use_pubsub: bool = False, use_bigquery: bool = False, use_gemini: bool = False):
        """Initialize pipeline components."""
        self.use_pubsub = use_pubsub
        self.use_bigquery = use_bigquery
        self.use_gemini = use_gemini
        
        # Initialize components
        self.ingestion = DataIngestionPipeline()
        
        self.storage = None
        if use_bigquery:
            try:
                self.storage = BigQueryStorage()
                print("✓ BigQuery storage initialized")
            except Exception as e:
                print(f"⚠ BigQuery initialization failed: {e}")
        
        self.analyzer = None
        if use_gemini:
            try:
                self.analyzer = GeminiAnalyzer()
                print("✓ Gemini analyzer initialized")
            except Exception as e:
                print(f"⚠ Gemini initialization failed: {e}")
        
        if use_pubsub:
            try:
                self.ingestion.setup_pubsub()
                print("✓ Pub/Sub configured")
            except Exception as e:
                print(f"⚠ Pub/Sub setup failed: {e}")
    
    def setup_infrastructure(self):
        """Setup BigQuery tables and Pub/Sub topics."""
        print("\n=== Setting up infrastructure ===")
        
        if self.use_pubsub:
            try:
                self.ingestion.setup_pubsub()
                print("✓ Pub/Sub topic created/verified")
            except Exception as e:
                print(f"✗ Pub/Sub setup failed: {e}")
        
        if self.storage:
            try:
                self.storage.setup_schema()
                print("✓ BigQuery schema created/verified")
            except Exception as e:
                print(f"✗ BigQuery setup failed: {e}")
    
    def run_batch_processing(self, num_events: int = 10):
        """Run a single batch of the pipeline."""
        print(f"\n=== Processing batch of {num_events} events ===")
        
        # Step 1: Ingest
        print("\n[1/4] Generating synthetic news events...")
        events = self.ingestion.generate_and_publish(count=num_events)
        print(f"✓ Generated {len(events)} events")
        
        # Step 2: Store raw events
        if self.storage:
            print("\n[2/4] Storing raw events in BigQuery...")
            try:
                self.storage.insert_raw_events(events)
                print(f"✓ Stored {len(events)} raw events")
            except Exception as e:
                print(f"✗ Storage failed: {e}")
        else:
            print("\n[2/4] Skipping BigQuery storage (not configured)")
        
        # Step 3: Analyze with Gemini
        analyzed_events = events
        if self.analyzer:
            print("\n[3/4] Analyzing events with Gemini Pro...")
            try:
                analyzed_events = self.analyzer.analyze_batch(events)
                print(f"✓ Analyzed {len(analyzed_events)} events")
            except Exception as e:
                print(f"✗ Analysis failed: {e}")
                print("Using fallback analysis...")
                analyzed_events = [self.analyzer._get_fallback_analysis(e) for e in events]
        else:
            print("\n[3/4] Skipping Gemini analysis (not configured)")
        
        # Step 4: Store analyzed events
        if self.storage:
            print("\n[4/4] Storing analyzed events in BigQuery...")
            try:
                self.storage.insert_analyzed_events(analyzed_events)
                print(f"✓ Stored {len(analyzed_events)} analyzed events")
            except Exception as e:
                print(f"✗ Storage failed: {e}")
        else:
            print("\n[4/4] Skipping analyzed data storage (not configured)")
        
        print("\n=== Batch processing complete ===")
        self._print_summary(analyzed_events)
        
        return analyzed_events
    
    def run_continuous(self, interval_seconds: int = 10, batch_size: int = 5):
        """Run continuous event processing."""
        print(f"\n=== Starting continuous processing ===")
        print(f"Batch size: {batch_size}, Interval: {interval_seconds}s")
        print("Press Ctrl+C to stop\n")
        
        import time
        
        try:
            while True:
                self.run_batch_processing(num_events=batch_size)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\nStopped continuous processing")
    
    def _print_summary(self, events):
        """Print summary of processed events."""
        if not events:
            return
        
        risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        
        for event in events:
            risk_level = event.get("risk_level", "MEDIUM")
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            sentiment = event.get("sentiment", "NEUTRAL")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        print("\n📊 Summary:")
        print(f"  Risk Levels: HIGH={risk_counts['HIGH']}, MEDIUM={risk_counts['MEDIUM']}, LOW={risk_counts['LOW']}")
        print(f"  Sentiments: NEG={sentiment_counts['NEGATIVE']}, NEU={sentiment_counts['NEUTRAL']}, POS={sentiment_counts['POSITIVE']}")


def main():
    """Main entry point with CLI arguments."""
    parser = argparse.ArgumentParser(description="ChainSight AI - Supply Chain Risk Intelligence Pipeline")
    parser.add_argument("--setup", action="store_true", help="Setup infrastructure (BigQuery, Pub/Sub)")
    parser.add_argument("--batch", type=int, default=10, help="Run batch processing with N events")
    parser.add_argument("--continuous", action="store_true", help="Run continuous processing")
    parser.add_argument("--interval", type=int, default=10, help="Interval between batches (seconds)")
    parser.add_argument("--pubsub", action="store_true", help="Enable Pub/Sub publishing")
    parser.add_argument("--bigquery", action="store_true", help="Enable BigQuery storage")
    parser.add_argument("--gemini", action="store_true", help="Enable Gemini analysis")
    parser.add_argument("--all", action="store_true", help="Enable all cloud services")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check if any cloud services are enabled
    use_pubsub = args.pubsub or args.all
    use_bigquery = args.bigquery or args.all
    use_gemini = args.gemini or args.all
    
    print("=" * 60)
    print("ChainSight AI - Supply Chain Risk Intelligence Platform")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Pub/Sub: {'✓ Enabled' if use_pubsub else '✗ Disabled (demo mode)'}")
    print(f"  BigQuery: {'✓ Enabled' if use_bigquery else '✗ Disabled (demo mode)'}")
    print(f"  Gemini: {'✓ Enabled' if use_gemini else '✗ Disabled (fallback mode)'}")
    
    # Initialize pipeline
    pipeline = ChainSightPipeline(
        use_pubsub=use_pubsub,
        use_bigquery=use_bigquery,
        use_gemini=use_gemini
    )
    
    # Execute requested operation
    if args.setup:
        pipeline.setup_infrastructure()
    elif args.continuous:
        pipeline.run_continuous(interval_seconds=args.interval, batch_size=args.batch)
    else:
        pipeline.run_batch_processing(num_events=args.batch)
    
    print("\n✓ Pipeline execution complete")


if __name__ == "__main__":
    main()
