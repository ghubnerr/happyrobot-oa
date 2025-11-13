# Inbound Carrier Sales Automation

A HappyRobot platform integration for automating inbound carrier load sales calls.

## Project Structure

```
happyrobot/
├── backend/          # FastAPI backend service
├── docs/            # HappyRobot platform documentation
└── docker-compose.yml
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLite, uv
- **Platform**: HappyRobot (for voice AI agent)

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+
- Docker & Docker Compose
- Terraform (for deployment)

### Development Setup

1. **Backend Setup**:

   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   uv run uvicorn app.main:app --reload --reload-exclude "**/.venv/**" --reload-exclude "**/__pycache__/**"
   ```

2. **Frontend Setup**:

   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Docker Setup**:
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

See `infrastructure/README.md` for GCP deployment instructions.
