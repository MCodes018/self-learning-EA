import json
from typing import Literal
import requests
from pydantic import BaseModel, Field
from ea.autonomy import choose_autonomy_mode
from ea.config import DATA_DIR
from ea.models import Action, Decision

class Out(BaseModel):
    priority: Literal["high","medium","low"]
    action: Action
    summary: str
    rationale: str
    confidence: float = Field(ge=0, le=1)
    risk: float = Field(ge=0, le=1)
    draft: str | None = None
    delegate_to: str | None = None

PROMPT = """You are the decision engine for an Executive Assistant at The Gen Academy.
Use only supplied work item, company context, user context, and learned guidance.
Explicit preferences outrank assumptions. Do not invent availability, relationships,
facts, preferences, or delegation targets. If information is insufficient choose ask.
Return JSON only with priority, action, summary, rationale, confidence, risk, draft, delegate_to.
priority is high/medium/low; action is reply/schedule/delegate/prioritize/archive/ask.
confidence and risk are numeric 0-1."""

class LLMPolicy:
    def __init__(self, key, model):
        if not key:
            raise ValueError("OPENAI_API_KEY is required when DECISION_POLICY=llm.")
        self.key=key; self.model=model
        self.endpoint="https://api.openai.com/v1/chat/completions"

    def decide(self, item, company, user, shadow):
        path=DATA_DIR/"optimized_action_prompt.txt"
        guidance=path.read_text(encoding="utf-8") if path.exists() else None
        payload={
            "work_item":item.model_dump(mode="json"),
            "company_context":company,
            "user_context":user,
            "learned_action_guidance":guidance,
        }
        response=requests.post(
            self.endpoint,
            headers={"Authorization":f"Bearer {self.key}","Content-Type":"application/json"},
            json={
                "model":self.model,
                "messages":[
                    {"role":"system","content":PROMPT},
                    {"role":"user","content":json.dumps(payload,ensure_ascii=False)},
                ],
                "response_format":{"type":"json_object"},
            },
            timeout=45,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"OpenAI HTTP {response.status_code}: {response.text[:500]}")
        parsed=Out.model_validate_json(response.json()["choices"][0]["message"]["content"])
        return Decision(
            event_id=item.event_id,
            **parsed.model_dump(),
            autonomy_mode=choose_autonomy_mode(parsed.confidence,parsed.risk,shadow),
            agent_version="llm-http-v2" if guidance else "llm-http-v1",
        )
