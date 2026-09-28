# Customer Support Agent with Hindsight Memory

A working AI support-agent demo that uses Groq and Hindsight memory to transform generic troubleshooting into personalized, context-aware assistance. The core request path is operational; the remaining production hardening work is listed below.

## 🎯 Project Overview

This hackathon project demonstrates how **persistent memory is central to the value proposition** of AI agents. Without memory, the agent is a generic chatbot. With Hindsight, it becomes a true support partner that:

- Recalls every customer interaction
- Identifies patterns in repeat issues
- Escalates intelligently based on history
- Prevents repeat problems proactively
- Learns which solutions work best for each customer

## Implementation Status

### Completed from the original brief

- FastAPI backend with health checks, OpenAPI docs, ticket creation, ticket resolution, customer profile, analytics, and memory-status endpoints.
- Streamlit operator console for new tickets, resolution capture, customer memory inspection, analytics, and backend status.
- Groq integration using the official async SDK with structured JSON output, model configuration, timeouts, and deterministic fallback when Groq is unavailable.
- Hindsight Cloud integration using the official `hindsight-client` package.
- Persistent Hindsight retain and recall for ticket interactions and resolutions, scoped with customer and ticket tags.
- Hindsight bank initialization and API-version health verification.
- Local in-memory fallback so the application remains runnable without external services.
- Escalation routing, urgency/frustration signals, resolution tracking, and basic analytics.
- Environment configuration, `.env` protection through `.gitignore`, and startup/shutdown handling for external clients.
- Regression and integration coverage: `4 passed`; live Groq and Hindsight smoke checks completed.

### Still required from the original brief

- Implement the missing synthetic data generator, Hindsight seed script, four-scenario demo runner, and comparative evaluation script described in the original brief.
- Persist structured customer profiles, repeat-issue patterns, and analytics in Hindsight rather than keeping those derived objects locally.
- Add authentication, authorization, rate limiting, request validation limits, and restricted production CORS.
- Add production observability: structured request logs, error tracking, metrics export, tracing, and alerts.
- Add Docker/Compose or deployment manifests, CI checks, secret-management guidance, and a production database/service runbook.
- Expand tests for remote Hindsight failures, Groq failures, retries, malformed provider responses, concurrent requests, and deployment configuration.
- Replace the current process-global memory client with lifecycle-managed dependency injection for multi-worker deployments.

The current system is demo-ready and externally integrated, but it should not be labeled fully production-ready until the remaining security, persistence, observability, deployment, and test work is complete.

## 📊 Demo Story: Interaction 1 → 50 Learning Curve

The live demo shows the same customer problem across 4 interactions:
- **Interaction 1** (cold start): Generic troubleshooting, 15 min resolution
- **Interaction 5** (pattern detection): Recognizes repeat issue, 5 min resolution
- **Interaction 20** (proactive): Predicts issue before customer reports, <2 min resolution
- **Interaction 50** (system learning): Uses aggregate data to predict infrastructure issues

## 🏗️ Architecture

```
Frontend (Streamlit) 
    ↓
FastAPI Backend (async)
    ↓
┌─────────────────────────────────────┐
│  Support Agent Pipeline             │
├─────────────────────────────────────┤
│ 1. Sentiment Analyzer               │
│ 2. Hindsight Memory Retriever       │
│ 3. Context-Aware Classifier        │
│ 4. Solution Generator              │
│ 5. Escalation Router               │
│ 6. Learning & Update Loop          │
└──────────────────┬──────────────────┘
                   ↓
        Hindsight Cloud (Memory)
        - Customer Profiles
        - Ticket History
        - Pattern Database
        - Solution Library
```

## 📁 Project Structure

```
customer_support_agent/
├── README.md (this file)
├── requirements.txt
├── .env.example
├── config.py
├── main.py (FastAPI entry point)
├── app/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── support_agent.py (main agent logic)
│   │   ├── sentiment_analyzer.py
│   │   ├── context_retriever.py
│   │   ├── solution_generator.py
│   │   └── escalation_router.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── hindsight_client.py (local fallback memory)
│   │   └── persistent_hindsight_client.py (Hindsight Cloud adapter)
│   ├── integrations/
│   │   └── groq_client.py (Groq integration)
│   ├── data/
│   │   └── (synthetic data planned)
│   └── api/
│       ├── __init__.py
│       ├── routes.py (API endpoints)
│       └── models.py (Pydantic schemas)
├── frontend/
│   ├── app.py (Streamlit UI)
│   └── components.py
├── tests/
│   ├── test_basic_app.py
│   └── test_groq_integration.py
└── scripts/
    ├── seed_database.py
  └── run_demo.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Groq API Key (free: https://groq.com/)
- Hindsight Cloud account with $50 credits (promo code: MEMHACK99)

### First-time setup

```bash
# Clone repo
git clone <repo>
cd customer_support_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys:
# GROQ_API_KEY=your_key
# HINDSIGHT_API_KEY=your_key
# HINDSIGHT_NAMESPACE=your_namespace
```

On Windows PowerShell:

```powershell
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and add GROQ_API_KEY and HINDSIGHT_API_KEY.
```

### Start the backend

Run this in terminal 1:

```powershell
& ".venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Backend URLs:

- API: http://localhost:8000
- Health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Start the user interface

Keep the backend running and open a second terminal:

```powershell
& ".venv\Scripts\python.exe" -m streamlit run frontend/app.py --server.port 8501
```

Open the operator console at http://localhost:8501.

The console includes ticket processing and resolution, customer memory inspection, analytics, and Hindsight status. Set `SUPPORT_API_URL` when the backend runs on a different host or port.

### Optional Local Mock Demo

```bash
# Runs three local in-memory example interactions
python scripts/run_demo.py
```

The current seed script is also a small local mock-memory example. It does not seed Hindsight Cloud. Cloud memories are created automatically when the API processes tickets with valid Hindsight settings in `.env`.

## 📋 Key Features

### 1. **Sentiment & Urgency Detection**
Analyzes customer message to detect frustration level and priority:
- High frustration → immediate escalation flag
- Low response time → proactive assistance
- Repeat issues → elevated urgency

### 2. **Hindsight Memory Retrieval**
Pulls from persistent memory:
- Customer profile (tier, history, churn risk)
- Past 20 tickets (searchable by category, date, sentiment)
- Issue patterns (this customer's common problems)
- Resolution patterns (what worked before)
- Escalation rules (who handles similar issues)

### 3. **Intelligent Classification**
Categorizes issue and finds similar past tickets:
- Issue categories: API, Billing, Account, Technical, Other
- Similarity matching to past resolutions
- Escalation trigger detection

### 4. **Context-Aware Generation**
Uses customer history to craft personalized responses:
- Acknowledges past issues
- References successful solutions
- Proactively suggests preventive actions
- Routes to right agent

### 5. **Escalation Intelligence**
Routes to human agents smartly:
- High-effort issues to specialists
- Recurring problems to original resolver
- High-value customers to dedicated support
- Frustrated customers to senior staff

### 6. **Continuous Learning**
Updates Hindsight after each interaction:
- Logs ticket resolution and outcome
- Recalculates success patterns
- Updates customer risk profile
- Learns escalation effectiveness

## 🔑 API Endpoints

### POST `/api/support/ticket`
Create a new support ticket

**Request:**
```json
{
  "customer_id": "cust_001",
  "message": "My API keeps timing out",
  "channel": "chat"
}
```

**Response:**
```json
{
  "ticket_id": "ticket_12345",
  "response": "I see this is the third timeout...",
  "memory_used": {
    "past_tickets_recalled": 3,
    "pattern_detected": "v2.8_revert",
    "escalation_suggested": false
  },
  "metadata": {
    "resolution_time_estimate": "5 min",
    "first_contact_resolution_probability": 0.85
  }
}
```

### GET `/api/customer/{customer_id}/profile`
Retrieve customer profile and memory

**Response:**
```json
{
  "customer_id": "cust_001",
  "profile": {...},
  "ticket_history": [...],
  "patterns": {...},
  "metrics": {
    "total_tickets": 23,
    "avg_resolution_time": "12 min",
    "satisfaction_score": 7.5,
    "churn_risk": "low"
  }
}
```

### POST `/api/memory/learn`
Update memory with resolution outcome

**Request:**
```json
{
  "ticket_id": "ticket_12345",
  "customer_id": "cust_001",
  "outcome": "resolved",
  "resolution_method": "api_upgrade_to_v3",
  "resolution_time_minutes": 5,
  "satisfaction_score": 9
}
```

### GET `/api/analytics/metrics`
Get live service metrics

**Response:**
```json
{
  "total_tickets": 1,
  "avg_resolution_time_minutes": 5.0,
  "repeat_issue_rate": 1.0,
  "customer_count": 1,
  "service_status": "healthy"
}
```

## 💾 Hindsight Memory Schema

Ticket conversations and resolutions are retained in the Hindsight bank configured by `HINDSIGHT_BANK_ID`. The adapter scopes memories with customer, ticket, category, and resolution tags.

The following logical records describe the information captured by the application; they are not separate Hindsight key-value namespaces.

### Customer Profile
```
customer:{customer_id}
{
  "profile": {
    "name", "email", "company", "tier",
    "joinDate", "totalTickets", "churnRisk"
  },
  "preferences": {
    "communicationStyle",
    "escalationThreshold",
    "preferredAgent"
  }
}
```

### Ticket Records
```
ticket:{customer_id}:{ticket_id}
{
  "date", "category", "severity",
  "description", "resolution",
  "resolvedTime", "satisfactionScore",
  "rootCause", "agentWhoSolved"
}
```

### Pattern Database
```
patterns:{customer_id}
{
  "commonIssues": [
    {"issue", "frequency", "avgResolution"}
  ],
  "successfulApproaches": [
    {"approach", "successRate"}
  ],
  "escalationHistory": [...]
}
```

### Solution Library
```
solution:{issue_category}:{customer_id}
{
  "approach", "steps", "expectedOutcome",
  "relevantPastTicket", "effectiveness"
}
```

## 📊 Synthetic Data

Synthetic customer and ticket generation is part of the original plan but is not implemented yet. The current `scripts/seed_database.py` creates only a few local mock records and does not seed Hindsight Cloud.

## 🎬 Current Demo

The current local script runs three simple mock-memory interactions. The original four-stage learning progression (cold start, repeat-pattern detection, proactive assistance, and institutional learning) still needs to be implemented.

Run the current mock demo with: `python scripts/run_demo.py`

## 📈 Metrics Dashboard

View live ticket and resolution metrics in the Streamlit operator console:

| Metric | Current source |
|--------|---|
| Ticket count | Hindsight-backed interactions plus local process metrics |
| Average resolution time | Recorded resolution outcomes |
| Repeat issue rate | Current resolution outcome ratio |
| Customer count | Customers seen by the running service |

Access dashboard:
```bash
python -m streamlit run frontend/app.py
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# LLM Settings
LLM_MODEL = "openai/gpt-oss-120b"  # Groq model
LLM_TEMPERATURE = 0.3  # Lower = more consistent
LLM_MAX_TOKENS = 1000

# Memory Settings
HINDSIGHT_BATCH_SIZE = 100
MEMORY_RETENTION_DAYS = 365
PATTERN_MIN_FREQUENCY = 2

# Agent Settings
ESCALATION_THRESHOLD_URGENCY = 0.8
ESCALATION_THRESHOLD_SATISFACTION = 4.0
MAX_RESOLUTION_TIME_MINUTES = 30

# Planned data settings
NUM_SYNTHETIC_CUSTOMERS = 50
NUM_SYNTHETIC_TICKETS = 500
```

## 🧪 Testing

Run tests to verify functionality:

```bash
pytest -q
```

## 📝 Implementation Notes

### Why Hindsight Over Regular Database?
- **Semantic search**: Find similar issues, not just keyword match
- **Vector embeddings**: Understand intent, not just text
- **Time-aware queries**: Weight recent patterns higher
- **Namespace isolation**: Clean separation of concerns
- **Built for learning**: Natural fit for ML agent memory

### LLM Choice (Groq)
- **Speed**: <100ms response time (critical for support)
- **Cost**: Generous free tier
- **Quality**: GPT-oss-120b is strong for instruction-following
- **Function calling**: Clean integration with agent actions

### Scaling Considerations
- Hindsight Cloud handles unlimited customers
- Consider caching hot customer data (tier/recent tickets)
- Batch pattern updates (not per-ticket)
- Archive old tickets after 1 year to keep queries fast

## 🚢 Deployment

### Deploy Backend (FastAPI)
```bash
# Using Render, Railway, or similar:
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Deploy Frontend (Streamlit)
```bash
# Using Streamlit Cloud:
# Push to GitHub, connect repo to Streamlit Cloud
```

### Environment Variables Required
```
GROQ_API_KEY=xxx
HINDSIGHT_API_KEY=xxx
HINDSIGHT_NAMESPACE=xxx
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=support_agent
```

## 📚 Resources

- [Hindsight Docs](https://hindsight.vectorize.io/)
- [Groq API Docs](https://console.groq.com/docs/speech-text)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)

## 👥 Team

- **Your Name** - Agent Architecture & Hindsight Integration
- **Your Name** - Frontend & Demo Flow
- **Your Name** - Data & Evaluation

## 📋 Submission Checklist

- [x] Clean, documented GitHub repo
- [ ] Demo video (60 sec hook + 3 min deep dive)
- [ ] Live demo to judges showing Interaction 1 → 20 progression
- [ ] Real-looking synthetic data (50+ customers, 500+ tickets)
- [ ] Comparative metrics showing measured memory ROI
- [ ] Content deliverables (article, social post, demo video)
- [x] Hindsight memory clearly central to the live ticket path

## 🎯 Key Success Metrics for Judges

The original target is to show clear learning progression:
1. **Interaction 1**: Generic response, 15 min resolution
2. **Interaction 5**: Recognizes pattern, 5 min resolution
3. **Interaction 20**: Proactive prediction, <2 min resolution

Judges will immediately see: "Without memory = generic chatbot. With memory = actual support partner."

---

**Ready to ship. Let's build something judges can't ignore.** 🚀
