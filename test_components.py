#!/usr/bin/env python3
"""
Quick test script to validate ChainSight AI components.
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv

def test_ingestion():
    """Test data ingestion module."""
    print("Testing Data Ingestion...")
    try:
        from src.ingestion import NewsGenerator, DataIngestionPipeline
        
        # Test news generator
        generator = NewsGenerator()
        event = generator.generate_event()
        
        assert "event_id" in event
        assert "headline" in event
        assert "company" in event
        
        # Test pipeline
        pipeline = DataIngestionPipeline()
        events = pipeline.generate_and_publish(count=3)
        
        assert len(events) == 3
        print("✓ Ingestion module working")
        return True
    except Exception as e:
        print(f"✗ Ingestion test failed: {e}")
        return False


def test_storage():
    """Test storage module (without actual GCP connection)."""
    print("\nTesting Storage Module...")
    try:
        from src.storage import BigQueryStorage
        
        # Test initialization (will fail without credentials, which is expected)
        try:
            storage = BigQueryStorage()
        except ValueError as e:
            # Expected when no GCP project ID is set
            print("  (Skipped - requires GCP configuration)")
        
        print("✓ Storage module imports successfully")
        return True
    except Exception as e:
        print(f"✗ Storage test failed: {e}")
        return False


def test_analysis():
    """Test analysis module (without actual Gemini API)."""
    print("\nTesting Analysis Module...")
    try:
        from src.analysis import GeminiAnalyzer, RiskAggregator
        
        # Test fallback analysis
        sample_event = {
            "event_id": "test_001",
            "timestamp": "2024-01-01T00:00:00",
            "headline": "Test disruption event",
            "company": "Test Corp",
            "location": "Test Location",
            "disruption_type": "labor",
            "expected_sentiment": "negative",
            "severity": "high"
        }
        
        # Test risk aggregator
        aggregator = RiskAggregator()
        summary = aggregator.aggregate_risks([sample_event])
        
        assert summary["total_events"] == 1
        print("✓ Analysis module working")
        return True
    except Exception as e:
        print(f"✗ Analysis test failed: {e}")
        return False


def test_visualization():
    """Test visualization module."""
    print("\nTesting Visualization Module...")
    try:
        from src.visualization import DashboardApp
        
        # Test import only (can't fully test streamlit without running it)
        app = DashboardApp()
        assert app is not None
        
        print("✓ Visualization module working")
        return True
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        return False


def test_utils():
    """Test utility functions."""
    print("\nTesting Utils...")
    try:
        from src.utils import (
            format_event_for_display,
            validate_event_schema,
            calculate_risk_score
        )
        
        test_event = {
            "event_id": "test_001",
            "timestamp": "2024-01-01T00:00:00",
            "headline": "Test event",
            "sentiment_score": -0.5,
            "risk_level": "HIGH"
        }
        
        # Test validation
        assert validate_event_schema(test_event) == True
        
        # Test formatting
        display = format_event_for_display(test_event)
        assert "test_001" in display
        
        # Test risk calculation
        risk_score = calculate_risk_score(test_event)
        assert 0 <= risk_score <= 1
        
        print("✓ Utils module working")
        return True
    except Exception as e:
        print(f"✗ Utils test failed: {e}")
        return False


def test_config():
    """Test configuration module."""
    print("\nTesting Configuration...")
    try:
        from config import config, AppConfig
        
        # Test config initialization
        app_config = AppConfig()
        assert app_config.gcp is not None
        
        print("✓ Configuration working")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    load_dotenv()
    
    print("=" * 60)
    print("ChainSight AI - Component Validation Tests")
    print("=" * 60)
    
    results = []
    results.append(("Configuration", test_config()))
    results.append(("Ingestion", test_ingestion()))
    results.append(("Storage", test_storage()))
    results.append(("Analysis", test_analysis()))
    results.append(("Visualization", test_visualization()))
    results.append(("Utils", test_utils()))
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:20s} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
