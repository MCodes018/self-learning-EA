import json
from ea.config import (
    FI_API_KEY, FI_SECRET_KEY, FUTUREAGI_ENABLED, FUTUREAGI_OBSERVE_ENABLED,
    FUTUREAGI_PROTECT_ENABLED, FUTUREAGI_PROJECT,
)

_PROVIDER = None

def ready():
    return FUTUREAGI_ENABLED and bool(FI_API_KEY and FI_SECRET_KEY)

def setup_observe():
    global _PROVIDER
    if not ready():
        return {"enabled": False, "reason": "Future AGI credentials not configured"}
    if not FUTUREAGI_OBSERVE_ENABLED:
        return {"enabled": False, "reason": "Observe disabled for local demo"}
    if _PROVIDER is not None:
        return {"enabled": True, "project": FUTUREAGI_PROJECT, "transport": "HTTP"}
    try:
        from fi_instrumentation import register, Transport
        from fi_instrumentation.fi_types import ProjectType
        _PROVIDER = register(
            project_type=ProjectType.OBSERVE,
            project_name=FUTUREAGI_PROJECT,
            transport=Transport.HTTP,
        )
        return {"enabled": True, "project": FUTUREAGI_PROJECT, "transport": "HTTP"}
    except Exception as exc:
        return {"enabled": False, "reason": str(exc)}

def protect_text(text):
    if not ready() or not FUTUREAGI_PROTECT_ENABLED:
        return {"enabled": False, "status": "skipped"}
    try:
        from fi.evals import Protect
        result = Protect().protect(
            inputs=text,
            protect_rules=[{"metric":"prompt_injection"},{"metric":"data_privacy_compliance"}],
            reason=True,
        )
        return {"enabled": True, **result}
    except Exception as exc:
        return {"enabled": True, "status": "error", "error": str(exc)}

def evaluate_record(record):
    if not ready():
        return {"enabled": False, "error": "Future AGI credentials not configured"}

    expected = record.user_action.value if record.user_action else None
    action_accuracy = float(record.agent_action.value == expected) if expected else None
    context = json.dumps({
        "event": record.event.model_dump(mode="json"),
        "company_context": record.context_snapshot.get("company", {}),
        "user_context": record.context_snapshot.get("user", {}),
    }, ensure_ascii=False)

    result = {
        "enabled": True,
        "action_accuracy": action_accuracy,
        "groundedness": None,
        "groundedness_reason": "",
    }
    try:
        from fi.evals import evaluate
        grounded = evaluate(
            "groundedness",
            input=record.event.body,
            context=context,
            output=record.agent_rationale,
            model="turing_flash",
        )
        result["groundedness"] = float(grounded.score) if grounded.score is not None else None
        result["groundedness_reason"] = grounded.reason or ""
    except Exception as exc:
        result["groundedness_error"] = str(exc)
    return result
