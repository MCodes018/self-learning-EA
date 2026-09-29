# The Gen Academy — Self-Learning Executive Assistant / Future AGI

Presentation prototype with TGA-branded Streamlit UI, LLM decisions, pending→resolved workflow, Activity history, read-only Gmail/Calendar/Slack, and Future AGI Observe/Evaluate/Protect/Optimize/Simulate.

## Run
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m pytest
streamlit run app.py
```

## Minimum demo `.env`
```env
DEMO_MODE=true
SHADOW_MODE=true
DECISION_POLICY=llm
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-luna
```

Cards disappear after resolution and move to Activity. Delete `data/decisions.jsonl` to reset demo history.

## Future AGI
```env
FUTUREAGI_ENABLED=true
FI_API_KEY=...
FI_SECRET_KEY=...
FUTUREAGI_PROJECT=TGA_EXECUTIVE_ASSISTANT
```
Restart Streamlit. Observe instruments OpenAI calls. Protect screens each work item for prompt injection/privacy. Each resolved decision runs Future AGI `accuracy` against the human action and `groundedness` on the rationale.

Learning → Optimize uses `agent-opt` on labeled human decisions. The winning action-selection prompt is saved to `data/optimized_action_prompt.txt` and is automatically included as learned guidance in subsequent LLM decisions.

For Simulation, create a Future AGI **chat simulation/run test** in the platform, then set its exact name:
```env
FUTUREAGI_SIMULATION_ID=My TGA EA Simulation
```
Learning → Simulate calls `agent-simulate` with this application as the callback agent. Future AGI stores transcripts, metrics and evals in its platform.

## Live connectors
Google: enable Gmail API + Calendar API, create an OAuth Desktop client, save as `client_secret.json`. The app requests read-only scopes and creates `token.json` after consent.

Slack: create a bot with read access to selected channels, add it to those channels, then set:
```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_IDS=C123,C456
```
Then switch:
```env
DEMO_MODE=false
SHADOW_MODE=true
```

## Future AGI features
- **Observe:** `fi-instrumentation-otel` + `traceAI-openai`, project registration and OpenAI auto-instrumentation.
- **Evaluate:** `ai-evaluation` with `accuracy` and `groundedness`.
- **Protect:** `Protect.protect()` with prompt-injection and data-privacy checks before LLM processing.
- **Optimize:** `agent-opt` MetaPrompt optimizer using resolved human actions as labels.
- **Simulate:** `agent-simulate` TestRunner using this EA as the chat callback.
- **Error Feed:** populated from Observe traces in the Future AGI platform; this app does not fabricate Error Feed results locally.
