# ChainSight AI Architecture

## System Overview

ChainSight AI is designed as a modular, production-ready platform for real-time supply chain risk intelligence. The architecture follows a pipeline pattern with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ChainSight AI Platform                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│   INGESTION     │      │   STORAGE    │      │    ANALYSIS     │
│                 │      │              │      │                 │
│  News Generator │──▶   │   BigQuery   │──▶   │   Gemini Pro    │
│  Pub/Sub Client │      │   Raw Table  │      │   AI Analyzer   │
│  Event Stream   │      │ Analyzed Tbl │      │   Risk Scorer   │
└─────────────────┘      └──────────────┘      └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │ VISUALIZATION   │
                                                │                 │
                                                │   Streamlit     │
                                                │   Dashboard     │
                                                │   Real-time UI  │
                                                └─────────────────┘
```

## Components

### 1. Ingestion Layer (`src/ingestion/`)

**Purpose**: Generate and publish supply chain news events

**Key Classes**:
- `NewsGenerator`: Creates realistic synthetic supply chain events
- `PubSubPublisher`: Publishes events to Google Cloud Pub/Sub
- `DataIngestionPipeline`: Orchestrates event generation and publishing

**Data Flow**:
1. Generate synthetic news events with metadata
2. Optionally publish to Pub/Sub topic
3. Return events for immediate processing

**Configuration**:
- Pub/Sub topic name
- Event generation parameters (frequency, types)

### 2. Storage Layer (`src/storage/`)

**Purpose**: Persist raw and analyzed data in BigQuery

**Key Classes**:
- `BigQueryStorage`: Manages all BigQuery operations

**Tables**:
1. **raw_news**: Original events as generated
   - event_id, timestamp, headline, company, location
   - disruption_type, severity, impact_area
   
2. **analyzed_news**: Events with AI analysis
   - All raw fields plus:
   - entities, sentiment, sentiment_score
   - risk_level, key_impacts, analysis_summary

**Data Flow**:
1. Create dataset and tables if not exist
2. Insert raw events immediately after generation
3. Insert analyzed events after Gemini processing
4. Query recent events for dashboard

### 3. Analysis Layer (`src/analysis/`)

**Purpose**: Extract insights using Gemini Pro AI

**Key Classes**:
- `GeminiAnalyzer`: Integrates with Gemini API
- `RiskAggregator`: Aggregates risk metrics

**Analysis Pipeline**:
1. Send event to Gemini with structured prompt
2. Parse JSON response
3. Extract entities, sentiment, risk level
4. Add fallback analysis if API fails
5. Return enriched event

**AI Outputs**:
- **Entities**: Companies, locations, products mentioned
- **Sentiment**: POSITIVE/NEUTRAL/NEGATIVE with score (-1 to +1)
- **Risk Level**: LOW/MEDIUM/HIGH
- **Key Impacts**: Specific supply chain effects
- **Summary**: Brief analysis text

### 4. Visualization Layer (`src/visualization/`)

**Purpose**: Real-time dashboard for risk monitoring

**Key Classes**:
- `DashboardApp`: Streamlit application

**Features**:
- **Metrics**: Total events, high-risk count, sentiment stats
- **Charts**: Risk distribution, sentiment analysis
- **Tables**: Recent events with full context
- **Filters**: Time range, risk level, location

**Data Sources**:
- Live mode: Query BigQuery for latest data
- Demo mode: Use synthetic sample data

## Data Flow

### Complete Pipeline Flow

```
1. GENERATE
   ├─ NewsGenerator creates event
   ├─ Add metadata (timestamp, IDs)
   └─ Return event object

2. PUBLISH (Optional)
   ├─ Serialize event to JSON
   ├─ Publish to Pub/Sub topic
   └─ Get message ID

3. STORE RAW
   ├─ Add ingested_at timestamp
   ├─ Insert into raw_news table
   └─ Confirm storage

4. ANALYZE
   ├─ Send to Gemini Pro
   ├─ Extract entities and sentiment
   ├─ Calculate risk level
   └─ Add analysis fields

5. STORE ANALYZED
   ├─ Add analyzed_at timestamp
   ├─ Insert into analyzed_news table
   └─ Confirm storage

6. VISUALIZE
   ├─ Query recent analyzed events
   ├─ Aggregate risk metrics
   ├─ Render dashboard
   └─ Auto-refresh
```

## Deployment Modes

### Demo Mode (Default)
- No cloud credentials required
- Local event generation
- Sample data visualization
- Perfect for development and testing

### Cloud Mode (Production)
- Requires GCP project and credentials
- Real Pub/Sub integration
- Persistent BigQuery storage
- Live Gemini AI analysis
- Scalable and production-ready

## Scalability Considerations

### Ingestion
- Pub/Sub handles 1000s of events/second
- Batch publishing for efficiency
- Async processing support

### Storage
- BigQuery auto-scales
- Partitioned tables for large datasets
- Streaming inserts for real-time data

### Analysis
- Gemini API has rate limits (check quotas)
- Batch processing with configurable size
- Fallback analysis for resilience

### Visualization
- Streamlit caches query results
- Configurable refresh intervals
- Pagination for large result sets

## Security Architecture

### Authentication
- Service account for GCP services
- API key for Gemini
- Environment variables for secrets

### Data Protection
- All data stays within GCP project
- Encryption at rest (BigQuery)
- Encryption in transit (HTTPS/TLS)

### Access Control
- IAM roles for least privilege
- Service account permissions
- VPC for network isolation (production)

## Extension Points

### Adding New Disruption Types
Edit `NewsGenerator.DISRUPTION_TYPES` in `pubsub_ingestion.py`

### Custom Analysis Logic
Extend `GeminiAnalyzer.analyze_news_event()` in `gemini_analyzer.py`

### Additional Visualizations
Add new methods to `DashboardApp` in `dashboard.py`

### Data Connectors
Create new storage modules following `BigQueryStorage` pattern

## Monitoring and Observability

### Logging
- Python logging throughout
- Console output for events
- Error tracking with exceptions

### Metrics
- Event counts per batch
- Analysis success/failure rates
- Dashboard query performance

### Alerts (Production)
- BigQuery query failures
- Pub/Sub publish errors
- Gemini API errors
- High risk event detection

## Performance Characteristics

### Throughput
- Ingestion: 100+ events/second
- Analysis: Limited by Gemini API (5-10/second typical)
- Storage: 1000s inserts/second (BigQuery streaming)
- Dashboard: Sub-second query responses

### Latency
- Event generation: <10ms
- Pub/Sub publish: 10-100ms
- BigQuery insert: 100-500ms
- Gemini analysis: 1-3 seconds
- Dashboard refresh: 1-2 seconds

## Cost Optimization

### BigQuery
- Use partitioned tables for large datasets
- Set table expiration for old data
- Use slots for predictable pricing

### Pub/Sub
- Batch messages when possible
- Use subscriptions efficiently
- Delete unused topics/subscriptions

### Gemini API
- Cache analysis results when possible
- Use fallback for non-critical events
- Batch requests where supported
