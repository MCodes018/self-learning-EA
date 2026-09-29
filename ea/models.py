from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

class Source(str, Enum):
    GMAIL="gmail"; CALENDAR="calendar"; SLACK="slack"

class Action(str, Enum):
    REPLY="reply"; SCHEDULE="schedule"; DELEGATE="delegate"; PRIORITIZE="prioritize"; ARCHIVE="archive"; ASK="ask"

class WorkItem(BaseModel):
    event_id: str
    source: Source
    title: str
    body: str
    sender: str | None = None
    timestamp: datetime
    metadata: dict = Field(default_factory=dict)

class Decision(BaseModel):
    event_id: str
    priority: Literal["high","medium","low"]
    action: Action
    summary: str
    rationale: str
    confidence: float = Field(ge=0, le=1)
    risk: float = Field(ge=0, le=1)
    autonomy_mode: Literal["act","propose","ask"]
    draft: str | None = None
    delegate_to: str | None = None
    agent_version: str = "prototype"

class DecisionRecord(BaseModel):
    event: WorkItem
    context_snapshot: dict = Field(default_factory=dict)
    agent_action: Action
    agent_priority: Literal["high","medium","low"]
    agent_summary: str
    agent_rationale: str
    agent_confidence: float = Field(ge=0, le=1)
    agent_risk: float = Field(ge=0, le=1)
    agent_version: str
    user_action: Action | None = None
    accepted: bool
    note: str | None = None
    status: Literal["resolved","dismissed"] = "resolved"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evals: dict = Field(default_factory=dict)
