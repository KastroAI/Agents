# Jaded Rose Core

Shared infrastructure and orchestration layer for the Jaded Rose multi-agent AI system. This repository provides the foundational services — configuration, database models, shared API clients, task routing, and scheduling — used by all Jaded Rose agents.

## System Diagram

```
                          ┌──────────────────────────────────────────────┐
                          │              INCOMING REQUESTS               │
                          │   Shopify Webhooks · Telegram · WhatsApp     │
                          └────────────────────┬─────────────────────────┘
                                               │
                                               ▼
                                 ┌─────────────────────────┐
                                 │    auth/                 │
                                 │    Webhook Validator     │
                                 │    (HMAC-SHA256)         │
                                 └────────────┬────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          orchestrator/                                      │
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌───────────────────────┐   │
│  │  AgentRouter     │───▶│  TaskQueue        │───▶│  GCP Pub/Sub          │   │
│  │  (route by type) │    │  (publish/sub)    │    │  jaded-rose-tasks     │   │
│  └─────────────────┘    └──────────────────┘    └───────────┬───────────┘   │
│                                                              │               │
│  ┌──────────────────────────────────────┐                    │               │
│  │  Scheduler (Cloud Scheduler)         │                    │               │
│  │  · Weekly report  — Mon 08:00 GMT    │                    │               │
│  │  · Daily sync     — 03:00 daily      │                    │               │
│  └──────────────────────────────────────┘                    │               │
└──────────────────────────────────────────────────────────────┼───────────────┘
                                                               │
                       ┌───────────────┬───────────────┬───────┴───────┐
                       ▼               ▼               ▼               ▼
              ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ ┌───────────┐
              │  chatbot     │ │  data        │ │ intelligence│ │ outreach  │
              │  _agent      │ │  _agent      │ │ _agent      │ │ _agent    │
              │              │ │              │ │             │ │           │
              │ Order track  │ │ Product sync │ │ Reports     │ │ B2B email │
              │ FAQs         │ │ Inventory    │ │ Trends      │ │ Follow-up │
              │ Product Q&A  │ │              │ │ Competitors │ │           │
              │ Returns      │ │              │ │             │ │           │
              └──────┬───────┘ └──────┬───────┘ └──────┬──────┘ └─────┬─────┘
                     │                │                │              │
                     └────────────────┴────────┬───────┴──────────────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             shared/                                         │
│                                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌───────────┐  │
│  │ OpenAIClient   │  │ PineconeClient │  │ ShopifyClient  │  │  Logger   │  │
│  │                │  │                │  │                │  │ (JSON)    │  │
│  │ · chat()       │  │ · upsert()     │  │ · get_order()  │  │           │  │
│  │ · embed()      │  │ · query()      │  │ · get_products│  │ agent_name│  │
│  │ · chat_with_   │  │ · delete()     │  │ · inventory   │  │ trace_id  │  │
│  │   tools()      │  │                │  │ · fulfillment │  │ timestamp │  │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘  └───────────┘  │
│          │                   │                   │                           │
└──────────┼───────────────────┼───────────────────┼───────────────────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
   ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
   │  OpenAI API  │   │  Pinecone    │   │  Shopify Admin   │
   │  GPT-4o      │   │  Vector DB   │   │  REST API        │
   │  Embeddings  │   │              │   │                  │
   └──────────────┘   └──────────────┘   └──────────────────┘

                          ┌──────────────────────────────────┐
                          │           database/               │
                          │                                   │
                          │  ┌─────────┐  ┌───────────────┐   │
                          │  │ Models  │  │ Cloud SQL     │   │
                          │  │         │  │ (PostgreSQL)  │   │
                          │  │ Order   │  │               │   │
                          │  │ Product │  │ pool_size=5   │   │
                          │  │ Chat    │  │ max_overflow  │   │
                          │  │ Session │  │ =10           │   │
                          │  │ Outreach│  │               │   │
                          │  │ Contact │  └───────┬───────┘   │
                          │  │ Weekly  │          │           │
                          │  │ Report  │          ▼           │
                          │  └─────────┘  ┌───────────────┐   │
                          │               │  GCP Cloud    │   │
                          │               │  SQL (PG)     │   │
                          │               └───────────────┘   │
                          └──────────────────────────────────┘
```

## Project Structure

```
jaded-rose-core/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Pydantic BaseSettings — all env vars
│   └── constants.py         # Agent names, namespaces, intents, platforms
├── shared/
│   ├── __init__.py
│   ├── pinecone_client.py   # Vector upsert/query/delete with retries
│   ├── openai_client.py     # Chat, embeddings, tool-use with backoff
│   ├── shopify_client.py    # Shopify Admin API (orders, products, inventory)
│   └── logger.py            # Structured JSON logging
├── database/
│   ├── __init__.py
│   ├── models.py            # SQLAlchemy ORM: Order, Product, ChatSession, etc.
│   ├── cloud_sql.py         # Engine, session factory, FastAPI dependency
│   └── migrations/
│       └── env.py           # Alembic migration environment
├── orchestrator/
│   ├── __init__.py
│   ├── agent_router.py      # Routes tasks to agents via Pub/Sub
│   ├── task_queue.py        # GCP Pub/Sub publish/subscribe
│   └── scheduler.py         # Cloud Scheduler: weekly report, daily sync
├── auth/
│   ├── __init__.py
│   └── webhook_validator.py # HMAC validation for Shopify, Telegram, WhatsApp
├── tests/
│   ├── __init__.py
│   ├── test_router.py       # AgentRouter unit tests (12 task types)
│   └── test_shopify_client.py # ShopifyClient tests with mocked HTTP
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

## Agents

| Agent | Constant | Handles |
|---|---|---|
| **Chatbot** | `chatbot_agent` | Order tracking, FAQs, product queries, returns, escalation |
| **Data** | `data_agent` | Shopify product sync, inventory sync |
| **Intelligence** | `intelligence_agent` | Weekly reports, trend analysis, competitor scraping |
| **Outreach** | `outreach_agent` | B2B email outreach, follow-up sequences |

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Database | PostgreSQL via GCP Cloud SQL |
| ORM & migrations | SQLAlchemy 2.0 + Alembic |
| Task queue | GCP Pub/Sub |
| Scheduling | GCP Cloud Scheduler |
| Vector search | Pinecone (serverless, cosine, 1536-dim) |
| LLM | OpenAI GPT-4o + text-embedding-3-small |
| E-commerce | Shopify Admin REST API (2024-01) |
| HTTP client | httpx |
| Retry logic | tenacity (exponential backoff) |
| Config | pydantic-settings + python-dotenv |
| Logging | python-json-logger (structured JSON) |
| Container | Python 3.11-slim Docker image |

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

# Generate a migration from ORM models
alembic revision --autogenerate -m "initial tables"

# Apply migrations
alembic upgrade head
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4o and embeddings |
| `PINECONE_API_KEY` | Yes | Pinecone vector DB API key |
| `PINECONE_ENVIRONMENT` | Yes | Pinecone serverless region (e.g. `us-east-1`) |
| `PINECONE_INDEX_NAME` | No | Index name (default: `jaded-rose`) |
| `SHOPIFY_STORE_URL` | Yes | Full store URL (e.g. `https://jaded-rose.myshopify.com`) |
| `SHOPIFY_ADMIN_API_KEY` | Yes | Shopify Admin API access token (`shpat_...`) |
| `SHOPIFY_STOREFRONT_TOKEN` | Yes | Shopify Storefront access token |
| `SHOPIFY_WEBHOOK_SECRET` | Yes | Shopify webhook HMAC secret |
| `GCP_PROJECT_ID` | Yes | Google Cloud project ID |
| `GCP_PUBSUB_TOPIC` | No | Pub/Sub topic name (default: `jaded-rose-tasks`) |
| `CLOUD_SQL_CONNECTION_STRING` | Yes | PostgreSQL URI (`postgresql+psycopg2://...`) |
| `REDIS_URL` | No | Redis URL (default: `redis://localhost:6379/0`) |

## Running Locally

```bash
# Start the API server
uvicorn main:app --reload --port 8080

# Run tests
pytest tests/ -v
```

## Module Reference

### `config/settings.py`

All configuration is loaded from environment variables (or `.env`) via Pydantic `BaseSettings`. Import the singleton:

```python
from config.settings import settings
print(settings.SHOPIFY_STORE_URL)
```

### `config/constants.py`

Named constants for agents, Pinecone namespaces, chat intents, and platforms:

```python
from config.constants import CHATBOT_AGENT, NS_PRODUCTS, ORDER_TRACKING, PLATFORM_SHOPIFY
```

### `shared/openai_client.py`

```python
from shared.openai_client import OpenAIClient

ai = OpenAIClient()

# Chat completion
reply = ai.chat(
    messages=[{"role": "user", "content": "What's trending?"}],
    system_prompt="You are a fashion assistant.",
)

# Generate embedding
vector = ai.embed("silk blouse summer collection")

# Chat with tool definitions
response = ai.chat_with_tools(messages, tools=[...], system_prompt="...")
```

### `shared/pinecone_client.py`

```python
from shared.pinecone_client import PineconeClient
from config.constants import NS_PRODUCTS

pc = PineconeClient()

# Upsert vectors
pc.upsert([("prod-1", embedding, {"title": "Silk Blouse"})], namespace=NS_PRODUCTS)

# Semantic search
results = pc.query(embedding, namespace=NS_PRODUCTS, top_k=5)

# Delete
pc.delete(["prod-1"], namespace=NS_PRODUCTS)
```

### `shared/shopify_client.py`

```python
from shared.shopify_client import ShopifyClient

shop = ShopifyClient()

order = shop.get_order(123456)
order = shop.get_order_by_name("#JR-4821")
products = shop.get_products(limit=50)
fulfillments = shop.get_fulfillment(order_id=123456)
shop.update_inventory(inventory_item_id=1, location_id=2, quantity=100)
```

### `orchestrator/agent_router.py`

```python
from orchestrator.agent_router import AgentRouter

router = AgentRouter()
result = router.route("order_tracking", {"order_id": "#JR-4821"})
# => {"agent": "chatbot_agent", "task_type": "order_tracking", "message_id": "..."}
```

### `orchestrator/task_queue.py`

```python
from orchestrator.task_queue import TaskQueue

queue = TaskQueue()
queue.publish("jaded-rose-tasks", {"task_type": "product_sync", "payload": {}})
queue.subscribe("my-subscription", callback=my_handler)
```

### `orchestrator/scheduler.py`

```python
from orchestrator.scheduler import Scheduler

scheduler = Scheduler()
scheduler.create_weekly_report_job()   # Every Monday 08:00 London
scheduler.create_daily_sync_job()      # Daily at 03:00 London
```

### `auth/webhook_validator.py`

```python
from auth.webhook_validator import validate_shopify_webhook

is_valid = validate_shopify_webhook(request_body=body, hmac_header=header)
```

### `database/models.py`

Five ORM models mapped to PostgreSQL tables:

| Model | Table | Key Fields |
|---|---|---|
| `Order` | `orders` | `shopify_order_id`, `customer_email`, `status`, `total_price` |
| `Product` | `products` | `shopify_product_id`, `title`, `sku`, `inventory_quantity`, `price` |
| `ChatSession` | `chat_sessions` | `channel`, `user_id`, `thread_id`, `last_active` |
| `OutreachContact` | `outreach_contacts` | `company_name`, `email`, `status`, `sent_at`, `replied_at` |
| `WeeklyReport` | `weekly_reports` | `week_start`, `week_end`, `total_units_sold`, `report_json` |

### `database/cloud_sql.py`

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database.cloud_sql import get_db

@app.get("/orders")
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()
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

### Pub/Sub

```bash
# Create the task topic
gcloud pubsub topics create jaded-rose-tasks

# Create subscriptions for each agent
gcloud pubsub subscriptions create chatbot-sub --topic=jaded-rose-tasks --filter='attributes.agent="chatbot_agent"'
gcloud pubsub subscriptions create data-sub --topic=jaded-rose-tasks --filter='attributes.agent="data_agent"'
```

### Cloud Scheduler

Register the recurring jobs programmatically:

```python
from orchestrator.scheduler import Scheduler
s = Scheduler()
s.create_weekly_report_job()
s.create_daily_sync_job()
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

Tests use `unittest.mock` to patch external services (Pub/Sub, Shopify HTTP, etc.) so no live credentials are needed.
