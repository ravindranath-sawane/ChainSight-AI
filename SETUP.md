# Setup Guide for ChainSight AI

This guide walks you through setting up ChainSight AI for both demo and production use.

## Table of Contents

1. [Quick Start (Demo Mode)](#quick-start-demo-mode)
2. [Production Setup (Cloud Mode)](#production-setup-cloud-mode)
3. [Google Cloud Platform Setup](#google-cloud-platform-setup)
4. [Gemini API Setup](#gemini-api-setup)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start (Demo Mode)

Demo mode requires **no cloud configuration** and is perfect for testing and development.

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/ravindranath-sawane/ChainSight-AI.git
cd ChainSight-AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the quick start script
chmod +x quickstart.sh
./quickstart.sh
```

Or manually:

```bash
# Run component tests
python test_components.py

# Generate sample events
python main.py --batch 10

# Launch dashboard
streamlit run src/visualization/dashboard.py
```

### What Works in Demo Mode

✅ Event generation with realistic data  
✅ Local data processing  
✅ Dashboard visualization  
✅ All core functionality  

❌ No cloud persistence  
❌ No real-time Pub/Sub  
❌ No Gemini AI analysis (uses fallback)  

---

## Production Setup (Cloud Mode)

Production mode enables all cloud features for a production-ready deployment.

### Prerequisites

- All demo mode prerequisites
- Google Cloud Platform account
- Gemini API access
- Basic knowledge of GCP

### Step-by-Step Setup

#### 1. Create Google Cloud Project

```bash
# Install gcloud CLI if not already installed
# Follow: https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create your-project-id
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable pubsub.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

#### 2. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create chainsight-ai \
    --display-name="ChainSight AI Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:chainsight-ai@your-project-id.iam.gserviceaccount.com" \
    --role="roles/pubsub.editor"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:chainsight-ai@your-project-id.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:chainsight-ai@your-project-id.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"

# Download service account key
gcloud iam service-accounts keys create ~/chainsight-key.json \
    --iam-account=chainsight-ai@your-project-id.iam.gserviceaccount.com
```

#### 3. Get Gemini API Key

Option A: Using Google AI Studio (Easiest)
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

Option B: Using Vertex AI
1. Enable Vertex AI API in your GCP project
2. Use project-based authentication (no separate key needed)

#### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

Update `.env`:

```env
# Your GCP Project ID
GCP_PROJECT_ID=your-project-id

# GCP Region (choose closest to you)
GCP_LOCATION=us-central1

# Path to service account key
GOOGLE_APPLICATION_CREDENTIALS=/home/user/chainsight-key.json

# Pub/Sub configuration (can keep defaults)
PUBSUB_TOPIC=supply-chain-news
PUBSUB_SUBSCRIPTION=supply-chain-news-sub

# BigQuery configuration (can keep defaults)
BQ_DATASET_ID=supply_chain_data
BQ_RAW_TABLE_ID=raw_news
BQ_ANALYZED_TABLE_ID=analyzed_news

# Gemini API Key
GEMINI_MODEL=gemini-pro
GEMINI_API_KEY=your-gemini-api-key-here
```

#### 5. Initialize Infrastructure

```bash
# Setup BigQuery tables and Pub/Sub topics
python main.py --setup --all
```

This will:
- Create BigQuery dataset
- Create raw_news and analyzed_news tables
- Create Pub/Sub topic and subscription

#### 6. Run Production Pipeline

```bash
# Process a single batch with all features
python main.py --batch 20 --all

# Run continuous processing
python main.py --continuous --interval 15 --batch 5 --all
```

#### 7. Launch Dashboard

```bash
# Start the Streamlit dashboard
streamlit run src/visualization/dashboard.py

# In the dashboard, select "Live BigQuery" mode
```

---

## Google Cloud Platform Setup

### Detailed Configuration

#### BigQuery Setup

```bash
# Create dataset manually (optional, script does this)
bq mk --dataset \
    --location=us-central1 \
    your-project-id:supply_chain_data

# View tables
bq ls supply_chain_data

# Query data
bq query --use_legacy_sql=false \
    'SELECT * FROM `your-project-id.supply_chain_data.analyzed_news` LIMIT 10'
```

#### Pub/Sub Setup

```bash
# Create topic manually (optional)
gcloud pubsub topics create supply-chain-news

# Create subscription
gcloud pubsub subscriptions create supply-chain-news-sub \
    --topic=supply-chain-news

# List topics
gcloud pubsub topics list

# Test publish
gcloud pubsub topics publish supply-chain-news \
    --message='{"test": "message"}'
```

### Cost Estimation

**Monthly costs for typical usage** (10,000 events/day):

| Service | Usage | Est. Cost |
|---------|-------|-----------|
| BigQuery | 1 GB storage, 10 GB queries | $0.05 |
| Pub/Sub | 300,000 messages | $0.40 |
| Gemini API | 10,000 requests | $0.00* |
| **Total** | | **~$0.45/month** |

*Free tier includes generous quota

---

## Gemini API Setup

### Option 1: Google AI Studio (Recommended for Development)

1. Visit https://makersuite.google.com/
2. Sign in with Google account
3. Click "Get API Key"
4. Create new API key
5. Copy key to `.env` file

**Limitations:**
- Rate limits apply
- Not for production use
- Personal use only

### Option 2: Vertex AI (Recommended for Production)

1. Enable Vertex AI API in GCP:
```bash
gcloud services enable aiplatform.googleapis.com
```

2. Update `src/analysis/gemini_analyzer.py` to use Vertex AI:
```python
# Use Vertex AI instead of API key
from google.cloud import aiplatform

aiplatform.init(project=config.gcp.project_id, location=config.gcp.location)
```

3. No separate API key needed (uses service account)

**Benefits:**
- Enterprise SLA
- Higher rate limits
- Integrated billing
- Better security

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```
ModuleNotFoundError: No module named 'google'
```

**Solution:**
```bash
pip install -r requirements.txt
```

#### 2. Authentication Errors

```
DefaultCredentialsError: Could not automatically determine credentials
```

**Solution:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"
```

Or add to `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key.json
```

#### 3. Permission Errors

```
403 Permission denied on resource project
```

**Solution:**
- Verify service account has required roles
- Check project ID is correct
- Ensure APIs are enabled

```bash
# Check current project
gcloud config get-value project

# List enabled APIs
gcloud services list --enabled
```

#### 4. BigQuery Quota Exceeded

```
Exceeded rate limits
```

**Solution:**
- Reduce batch size
- Increase interval between batches
- Use batch inserts instead of streaming

#### 5. Gemini API Rate Limits

```
429 Too Many Requests
```

**Solution:**
- Reduce analysis batch size
- Add delays between requests
- Use fallback analysis for non-critical events

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system details
2. Review error messages carefully
3. Check GCP quotas and limits
4. Verify all APIs are enabled
5. Test with demo mode first

### Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed
- [ ] GCP project created
- [ ] Service account created with permissions
- [ ] Service account key downloaded
- [ ] Gemini API key obtained
- [ ] .env file configured
- [ ] Infrastructure setup completed
- [ ] Test batch runs successfully
- [ ] Dashboard loads

---

## Next Steps

After setup:

1. **Test the system**: Run a small batch and verify results
2. **Monitor costs**: Check GCP billing dashboard
3. **Tune parameters**: Adjust batch sizes and intervals
4. **Explore dashboard**: Familiarize yourself with visualizations
5. **Customize**: Add your own disruption types and analysis logic

## Additional Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
