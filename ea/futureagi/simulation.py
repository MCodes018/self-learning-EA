import asyncio, requests
from ea.config import FUTUREAGI_SIMULATION_ID,OPENAI_API_KEY,OPENAI_MODEL

def run_simulation():
    if not FUTUREAGI_SIMULATION_ID:
        return {"ok":False,"message":"Set FUTUREAGI_SIMULATION_ID to the exact Future AGI chat run-test name."}
    try:
        from fi.simulate import TestRunner
    except Exception as exc:
        return {"ok":False,"message":f"agent-simulate is not installed: {exc}"}

    async def callback(inp):
        latest=(inp.new_message or {}).get("content","") or ""
        def call():
            r=requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization":f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"},
                json={
                    "model":OPENAI_MODEL,
                    "messages":[
                        {"role":"system","content":"You are The Gen Academy executive assistant. Respond concisely and follow the executive preferences supplied by the simulator."},
                        {"role":"user","content":latest},
                    ],
                },timeout=60,
            )
            if r.status_code>=400: raise RuntimeError(f"OpenAI HTTP {r.status_code}: {r.text[:400]}")
            return r.json()["choices"][0]["message"]["content"] or ""
        return await asyncio.to_thread(call)

    async def go():
        return await TestRunner().run_test(
            run_test_name=FUTUREAGI_SIMULATION_ID,
            agent_callback=callback,concurrency=1,
        )
    try:
        asyncio.run(go())
        return {"ok":True,"message":"Simulation completed. Open Future AGI Simulate to inspect transcripts and eval metrics."}
    except Exception as exc:
        return {"ok":False,"message":f"Simulation failed: {exc}"}
