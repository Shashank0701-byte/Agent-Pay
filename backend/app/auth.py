import hashlib

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Agent

bearer_scheme = HTTPBearer(auto_error=False)


def get_agent_from_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Agent | None:
    if credentials is None or not credentials.credentials:
        return None

    api_key = credentials.credentials
    expected_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    agent = db.scalar(select(Agent).where(Agent.api_key_hash == expected_hash))
    if agent is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")
    if agent.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="agent disabled")
    return agent
