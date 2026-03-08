# Jaded Rose Core

Shared infrastructure and orchestration layer for the Jaded Rose multi-agent AI system. This repository provides the foundational services — configuration, database models, shared API clients, task routing, and scheduling — used by all Jaded Rose agents.

## Architecture

```
jaded-rose-core/
├── config/          # Settings (env vars) and constants
├── shared/          # Pinecone, OpenAI, Shopify clients & logger
├── database/        # SQLAlchemy models, Cloud SQL engine, Alembic migrations
├── orchestrator/    # Agent router, Pub/Sub task queue, Cloud Scheduler
├── auth/            # Webhook signature validation
└── tests/           # Unit tests
```

### Agents

| Agent | Purpose |
|---|---|
| `chatbot_agent` | Customer-facing chat (order tracking, FAQs, product queries) |
| `data_agent` | Shopify product & inventory sync |
| `intelligence_agent` | Weekly reports, trend analysis, competitor research |
| `outreach_agent` | B2B email outreach and follow-ups |

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (local or GCP Cloud SQL)
- GCP project with Pub/Sub and Cloud Scheduler enabled
- Pinecone account
- OpenAI API key
- Shopify store with Admin API access

### Installation

```bash
# Clone the repository
git clone https://github.com/Jaded-Rose/jaded-rose-core.git
cd jaded-rose-core

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Database Setup

```bash
# Initialise Alembic (first time only)
alembic init database/migrations

# Generate a migration
alembic revision --autogenerate -m "initial tables"

# Apply migrations
alembic upgrade head
```

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o and embeddings |
| `PINECONE_API_KEY` | Pinecone vector DB API key |
| `PINECONE_ENVIRONMENT` | Pinecone environment / region |
| `PINECONE_INDEX_NAME` | Name of the Pinecone index |
| `SHOPIFY_STORE_URL` | Shopify store URL |
| `SHOPIFY_ADMIN_API_KEY` | Shopify Admin API access token |
| `SHOPIFY_STOREFRONT_TOKEN` | Shopify Storefront access token |
| `SHOPIFY_WEBHOOK_SECRET` | Shopify webhook HMAC secret |
| `GCP_PROJECT_ID` | Google Cloud project ID |
| `GCP_PUBSUB_TOPIC` | Pub/Sub topic for task routing |
| `CLOUD_SQL_CONNECTION_STRING` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection URL |

## Running Locally

```bash
# Start the API server
uvicorn main:app --reload --port 8080

# Run tests
pytest tests/ -v
```

## Deploying to GCP

### Cloud Run

```bash
# Build and push the container
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/jaded-rose-core

# Deploy to Cloud Run
gcloud run deploy jaded-rose-core \
  --image gcr.io/$GCP_PROJECT_ID/jaded-rose-core \
  --platform managed \
  --region europe-west2 \
  --allow-unauthenticated \
  --set-env-vars "$(cat .env | grep -v '^#' | xargs | tr ' ' ',')"
```

### Cloud SQL

1. Create a Cloud SQL PostgreSQL instance in your GCP project.
2. Set `CLOUD_SQL_CONNECTION_STRING` to the instance connection string.
3. Run Alembic migrations against the Cloud SQL instance.

### Cloud Scheduler

The `Scheduler` class creates recurring jobs automatically. Run once to register them:

```python
from orchestrator.scheduler import Scheduler
s = Scheduler()
s.create_weekly_report_job()
s.create_daily_sync_job()
```
