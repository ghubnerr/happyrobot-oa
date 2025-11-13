# Inbound Carrier Sales Automation

A HappyRobot platform integration for automating inbound carrier load sales calls.

## Project Structure

```
happyrobot-oa/
├── backend/                    # FastAPI backend service
│   ├── app/                    
│   │   ├── config.py           # Application settings & environment variables
│   │   ├── database.py         # SQLAlchemy database setup
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── retrievers.py       # Hybrid BM25 + embedding search
│   │   ├── schemas.py          # Pydantic request/response schemas
│   │   └── routers/            # API route handlers
│   │       ├── __init__.py
│   │       ├── fmcsa.py        # FMCSA carrier verification
│   │       ├── loads.py        # Load search & management
│   │       └── metrics.py      # Call metrics & analytics
│   ├── scripts/                
│   │   ├── __init__.py
│   │   └── seed_loads.py       # Database seeding script
│   ├── tests/                  
│   │   ├── __init__.py
│   │   └── test_neural_search.py
│   └── uv.lock                 
├── Dockerfile                  # Build config
└── fly.toml                    # Fly.io deployment config
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLite, uv, sequence_transformers, rank_bm25
- **Platform**: HappyRobot Workflow

## Quick Start

   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   uv run uvicorn app.main:app --reload --reload-exclude "**/.venv/**" --reload-exclude "**/__pycache__/**"
   ```
 **Docker Setup**:
   ```bash
   docker-compose up --build
   ```

## API Documentation

Once the backend is running, visit:

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` files in backend and frontend directories.

## Deployment

Currently deployed to [https://happyrobot-oa.fly.dev](https://happyrobot-oa.fly.dev). See [health status here](https://happyrobot-oa.fly.dev/health).
