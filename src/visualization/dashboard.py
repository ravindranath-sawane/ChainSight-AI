"""
Streamlit Dashboard for ChainSight AI.
Real-time supply chain risk intelligence visualization.
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from storage.bigquery_storage import BigQueryStorage
    from analysis.gemini_analyzer import RiskAggregator
    BIGQUERY_AVAILABLE = True
except Exception as e:
    BIGQUERY_AVAILABLE = False
    print(f"BigQuery not available: {e}")


class DashboardApp:
    """Main dashboard application."""
    
    def __init__(self):
        """Initialize dashboard."""
        st.set_page_config(
            page_title="ChainSight AI - Supply Chain Risk Intelligence",
            page_icon="🔗",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        self.storage = None
        if BIGQUERY_AVAILABLE:
            try:
                self.storage = BigQueryStorage()
            except Exception as e:
                st.warning(f"BigQuery connection failed: {e}")
    
    def run(self):
        """Run the dashboard application."""
        # Header
        st.title("🔗 ChainSight AI")
        st.markdown("### Real-time Supply Chain Risk Intelligence Platform")
        st.markdown("---")
        
        # Sidebar
        with st.sidebar:
            st.header("⚙️ Settings")
            
            # Data source selection
            data_mode = st.radio(
                "Data Source",
                ["Demo Mode", "Live BigQuery"],
                help="Demo mode uses sample data, Live mode connects to BigQuery"
            )
            
            # Refresh button
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
            
            st.markdown("---")
            st.markdown("### About")
            st.markdown("""
            **ChainSight AI** detects financial and labor disruptions 
            in global supply chains using:
            - 📊 Google BigQuery
            - 🤖 Gemini Pro AI
            - 📡 Cloud Pub/Sub
            - 📈 Real-time Analytics
            """)
        
        # Load data
        if data_mode == "Live BigQuery" and self.storage:
            events = self._load_live_data()
        else:
            events = self._load_demo_data()
        
        if not events:
            st.warning("No data available. Generate some events first!")
            st.info("Run the ingestion pipeline to generate supply chain news events.")
            return
        
        # Main dashboard layout
        self._render_metrics(events)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_risk_distribution(events)
            st.markdown("---")
            self._render_top_entities(events)
        
        with col2:
            self._render_sentiment_analysis(events)
            st.markdown("---")
            self._render_geographic_distribution(events)
        
        st.markdown("---")
        self._render_recent_events(events)
    
    def _load_live_data(self) -> List[Dict]:
        """Load data from BigQuery."""
        try:
            events = self.storage.query_recent_events(
                table_name="analyzed_news",
                limit=100
            )
            return events
        except Exception as e:
            st.error(f"Error loading live data: {e}")
            return []
    
    def _load_demo_data(self) -> List[Dict]:
        """Load demo data for testing."""
        demo_events = [
            {
                "event_id": "demo_001",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "headline": "GlobalTech Corp faces strike action in Shanghai, China, causing significant supply chain delays.",
                "company": "GlobalTech Corp",
                "location": "Shanghai, China",
                "disruption_type": "labor",
                "sentiment": "NEGATIVE",
                "sentiment_score": -0.7,
                "risk_level": "HIGH",
                "entities": json.dumps(["GlobalTech Corp", "Shanghai", "China"]),
                "key_impacts": json.dumps(["Production delays", "Logistics disruption"])
            },
            {
                "event_id": "demo_002",
                "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
                "headline": "TransWorld Logistics successfully resolves equipment failure in Rotterdam, Netherlands.",
                "company": "TransWorld Logistics",
                "location": "Rotterdam, Netherlands",
                "disruption_type": "operational",
                "sentiment": "POSITIVE",
                "sentiment_score": 0.6,
                "risk_level": "LOW",
                "entities": json.dumps(["TransWorld Logistics", "Rotterdam", "Netherlands"]),
                "key_impacts": json.dumps(["Service restoration", "Improved reliability"])
            },
            {
                "event_id": "demo_003",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "headline": "Pacific Manufacturing reports credit rating downgrade affecting operations in Los Angeles, USA.",
                "company": "Pacific Manufacturing",
                "location": "Los Angeles, USA",
                "disruption_type": "financial",
                "sentiment": "NEGATIVE",
                "sentiment_score": -0.8,
                "risk_level": "HIGH",
                "entities": json.dumps(["Pacific Manufacturing", "Los Angeles", "USA"]),
                "key_impacts": json.dumps(["Financial constraints", "Operational impact"])
            },
            {
                "event_id": "demo_004",
                "timestamp": (datetime.now() - timedelta(hours=8)).isoformat(),
                "headline": "EuroSupply Chain announces port congestion in Hamburg, Germany, monitoring situation closely.",
                "company": "EuroSupply Chain",
                "location": "Hamburg, Germany",
                "disruption_type": "environmental",
                "sentiment": "NEUTRAL",
                "sentiment_score": 0.0,
                "risk_level": "MEDIUM",
                "entities": json.dumps(["EuroSupply Chain", "Hamburg", "Germany"]),
                "key_impacts": json.dumps(["Shipping delays", "Route adjustments"])
            },
            {
                "event_id": "demo_005",
                "timestamp": (datetime.now() - timedelta(hours=12)).isoformat(),
                "headline": "AsiaLink Industries faces labor shortage in Singapore, impacting delivery schedules.",
                "company": "AsiaLink Industries",
                "location": "Singapore",
                "disruption_type": "labor",
                "sentiment": "NEGATIVE",
                "sentiment_score": -0.5,
                "risk_level": "MEDIUM",
                "entities": json.dumps(["AsiaLink Industries", "Singapore"]),
                "key_impacts": json.dumps(["Workforce shortage", "Delivery delays"])
            }
        ]
        return demo_events
    
    def _render_metrics(self, events: List[Dict]):
        """Render top-level metrics."""
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate metrics
        total_events = len(events)
        high_risk = sum(1 for e in events if e.get("risk_level") == "HIGH")
        negative_sentiment = sum(1 for e in events if e.get("sentiment") == "NEGATIVE")
        avg_sentiment = sum(e.get("sentiment_score", 0) for e in events) / total_events if total_events > 0 else 0
        
        with col1:
            st.metric("Total Events", total_events)
        
        with col2:
            st.metric("High Risk Events", high_risk, delta=f"{(high_risk/total_events*100):.0f}%" if total_events > 0 else "0%")
        
        with col3:
            st.metric("Negative Sentiment", negative_sentiment, delta=f"{(negative_sentiment/total_events*100):.0f}%" if total_events > 0 else "0%")
        
        with col4:
            sentiment_label = "Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral"
            st.metric("Avg Sentiment", f"{avg_sentiment:.2f}", delta=sentiment_label)
    
    def _render_risk_distribution(self, events: List[Dict]):
        """Render risk level distribution chart."""
        st.subheader("📊 Risk Level Distribution")
        
        risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for event in events:
            risk_level = event.get("risk_level", "MEDIUM")
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        df = pd.DataFrame({
            "Risk Level": list(risk_counts.keys()),
            "Count": list(risk_counts.values())
        })
        
        st.bar_chart(df.set_index("Risk Level"))
    
    def _render_sentiment_analysis(self, events: List[Dict]):
        """Render sentiment analysis chart."""
        st.subheader("💭 Sentiment Analysis")
        
        sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        for event in events:
            sentiment = event.get("sentiment", "NEUTRAL")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        df = pd.DataFrame({
            "Sentiment": list(sentiment_counts.keys()),
            "Count": list(sentiment_counts.values())
        })
        
        st.bar_chart(df.set_index("Sentiment"))
    
    def _render_top_entities(self, events: List[Dict]):
        """Render top entities affected."""
        st.subheader("🏢 Top Affected Companies")
        
        company_counts = {}
        for event in events:
            company = event.get("company", "Unknown")
            company_counts[company] = company_counts.get(company, 0) + 1
        
        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for company, count in top_companies:
            st.write(f"**{company}**: {count} events")
    
    def _render_geographic_distribution(self, events: List[Dict]):
        """Render geographic distribution."""
        st.subheader("🌍 Geographic Distribution")
        
        location_counts = {}
        for event in events:
            location = event.get("location", "Unknown")
            location_counts[location] = location_counts.get(location, 0) + 1
        
        top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for location, count in top_locations:
            st.write(f"**{location}**: {count} events")
    
    def _render_recent_events(self, events: List[Dict]):
        """Render recent events table."""
        st.subheader("📰 Recent Events")
        
        # Sort by timestamp
        sorted_events = sorted(
            events,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )[:10]
        
        # Create DataFrame
        df_data = []
        for event in sorted_events:
            df_data.append({
                "Timestamp": event.get("timestamp", "")[:19],
                "Company": event.get("company", ""),
                "Location": event.get("location", ""),
                "Risk": event.get("risk_level", ""),
                "Sentiment": event.get("sentiment", ""),
                "Headline": event.get("headline", "")[:80] + "..."
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)


def main():
    """Main entry point."""
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()
