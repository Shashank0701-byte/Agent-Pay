# AgentPay

AgentPay is an agentic payment orchestration layer that lets AI agents request and execute payments under configurable user policies.

## Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Pytest

## Local setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker compose up --build
```

## Health check

```bash
curl http://localhost:8000/health
```

## Project goals

- secure agent identity and key management
- deterministic policy evaluation
- human approval for large or unusual charges
- Razorpay-backed payment execution
- auditable transaction ledger
- agent resume after payment completion
