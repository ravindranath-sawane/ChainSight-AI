# 🔗 ChainSight AI

**Real-time Supply Chain Risk Intelligence Platform**

ChainSight AI is a production-ready platform that detects and analyzes financial and labor disruptions in global supply chains using Google Cloud services and Gemini AI.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Powered-4285F4)
![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Enhanced-orange)

## 🎯 Features

- **Real-time Data Ingestion**: Synthetic supply chain news stream via Google Cloud Pub/Sub
- **Scalable Storage**: Raw JSON data stored in BigQuery for analytics
- **AI-Powered Analysis**: Gemini Pro extracts entities, sentiment, and risk levels
- **Live Visualization**: Interactive Streamlit dashboard with real-time risk metrics
- **Modular Architecture**: Production-ready, maintainable code structure
- **Demo Mode**: Run without cloud services for local testing and development

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Data Source   │      │   Storage    │      │    Analysis     │
│                 │      │              │      │                 │
│  Synthetic News │─────▶│   BigQuery   │─────▶│   Gemini Pro    │
│   (Pub/Sub)     │      │ (Raw + Data) │      │ Entity + Senti. │
└─────────────────┘      └──────────────┘      └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  Visualization  │
                                                │                 │
                                                │    Streamlit    │
                                                │    Dashboard    │
                                                └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Project (optional for demo mode)
- Gemini API Key (optional for AI analysis)

### For Production Use:
- Google Cloud Platform account
- Service account with permissions for:
  - Pub/Sub (Publisher/Subscriber)
  - BigQuery (Data Editor, Job User)
  - Vertex AI (User)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/ravindranath-sawane/ChainSight-AI.git
cd ChainSight-AI

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Optional: Only needed for production mode
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Run in Demo Mode

**No cloud configuration needed!**

```bash
# Generate sample events
python main.py --batch 10

# View the dashboard
streamlit run src/visualization/dashboard.py
```

### 4. Run with Cloud Services

```bash
# Setup infrastructure (first time only)
python main.py --setup --all

# Run single batch with all services
python main.py --batch 20 --all

# Run continuous processing
python main.py --continuous --interval 15 --batch 5 --all
```

## 📁 Project Structure

```
ChainSight-AI/
├── config.py                   # Configuration management
├── main.py                     # Main pipeline orchestrator
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
│
├── src/
│   ├── ingestion/             # Data ingestion module
│   │   └── pubsub_ingestion.py    # Pub/Sub integration & news generation
│   │
│   ├── storage/               # Storage module
│   │   └── bigquery_storage.py    # BigQuery integration
│   │
│   ├── analysis/              # Analysis module
│   │   └── gemini_analyzer.py     # Gemini AI integration
│   │
│   └── visualization/         # Visualization module
│       └── dashboard.py           # Streamlit dashboard
│
└── README.md
```

## 💻 Usage Examples

### Generate Events

```bash
# Generate 10 events (demo mode)
python main.py --batch 10

# Generate 50 events with BigQuery storage
python main.py --batch 50 --bigquery

# Generate events with full AI analysis
python main.py --batch 20 --gemini --bigquery
```

### Continuous Processing

```bash
# Process 5 events every 10 seconds
python main.py --continuous --batch 5 --interval 10 --all
```

### View Dashboard

```bash
# Launch Streamlit dashboard
streamlit run src/visualization/dashboard.py
```

The dashboard will open at `http://localhost:8501`

## 🔧 Module Details

### 1. Data Ingestion (`src/ingestion/`)

Generates realistic synthetic supply chain news events covering:
- **Disruption Types**: Financial, Labor, Operational, Environmental
- **Companies**: Global logistics and manufacturing companies
- **Locations**: Major supply chain hubs worldwide
- **Severity Levels**: Low, Medium, High

```python
from src.ingestion import DataIngestionPipeline

pipeline = DataIngestionPipeline()
events = pipeline.generate_and_publish(count=10)
```

### 2. Storage (`src/storage/`)

Manages BigQuery storage with two tables:
- **raw_news**: Original events with metadata
- **analyzed_news**: Events with AI analysis results

```python
from src.storage import BigQueryStorage

storage = BigQueryStorage()
storage.setup_schema()
storage.insert_raw_events(events)
```

### 3. Analysis (`src/analysis/`)

Uses Gemini Pro to extract:
- **Entities**: Companies, locations, products
- **Sentiment**: Positive, Neutral, Negative (with scores)
- **Risk Level**: Low, Medium, High
- **Key Impacts**: Specific supply chain effects

```python
from src.analysis import GeminiAnalyzer

analyzer = GeminiAnalyzer()
analyzed_events = analyzer.analyze_batch(events)
```

### 4. Visualization (`src/visualization/`)

Interactive Streamlit dashboard featuring:
- Real-time metrics (total events, high-risk count)
- Risk level distribution charts
- Sentiment analysis visualization
- Top affected companies and locations
- Recent events table

## 🎨 Dashboard Features

The Streamlit dashboard provides:

1. **Key Metrics**
   - Total events processed
   - High-risk event count
   - Negative sentiment events
   - Average sentiment score

2. **Risk Analysis**
   - Risk level distribution (Low/Medium/High)
   - Sentiment breakdown (Positive/Neutral/Negative)

3. **Geographic Intelligence**
   - Top affected locations
   - Company-wise event distribution

4. **Event Timeline**
   - Recent events with full context
   - Filterable and sortable table

## 🛠️ Development

### Running Individual Modules

```python
# Test ingestion
python -m src.ingestion.pubsub_ingestion

# Test storage
python -m src.storage.bigquery_storage

# Test analysis
python -m src.analysis.gemini_analyzer
```

### Demo Mode vs Production Mode

**Demo Mode** (default):
- No cloud credentials required
- Generates synthetic data locally
- Perfect for testing and development

**Production Mode**:
- Requires GCP credentials and API keys
- Real-time Pub/Sub integration
- Persistent BigQuery storage
- AI-powered analysis with Gemini

## 📊 Sample Output

```
=== Processing batch of 10 events ===

[1/4] Generating synthetic news events...
✓ Generated 10 events

[2/4] Storing raw events in BigQuery...
✓ Stored 10 raw events

[3/4] Analyzing events with Gemini Pro...
Analyzing event 1/10: evt_1234567890_1234
Analyzing event 2/10: evt_1234567890_5678
...
✓ Analyzed 10 events

[4/4] Storing analyzed events in BigQuery...
✓ Stored 10 analyzed events

📊 Summary:
  Risk Levels: HIGH=3, MEDIUM=5, LOW=2
  Sentiments: NEG=6, NEU=2, POS=2
```

## 🔐 Security Best Practices

- Store credentials in `.env` file (never commit to git)
- Use service accounts with minimal required permissions
- Rotate API keys regularly
- Enable audit logging in GCP
- Use VPC Service Controls for production deployments

## 📈 Performance Considerations

- **Ingestion**: Handles 1000+ events/minute
- **Storage**: BigQuery auto-scales for high throughput
- **Analysis**: Gemini API rate limits apply (consider batch sizing)
- **Dashboard**: Efficient queries with caching for real-time updates

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Cloud Platform for infrastructure services
- Google Gemini AI for intelligent analysis
- Streamlit for visualization framework

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review sample code in module files

---

**Built with ❤️ for supply chain resilience**