from concurrent.futures import ThreadPoolExecutor, as_completed
from ea.config import *
from ea.context import ContextStore
from ea.connectors.demo import DemoSource
from ea.policy import HeuristicPolicy
from ea.records import DecisionStore
from ea.futureagi.runtime import setup_observe, protect_text
from ea.models import Action, Decision
from ea.autonomy import choose_autonomy_mode

class EAService:
    def __init__(self):
        self.observe=setup_observe()
        self.ctx=ContextStore(USER_ID)
        self.store=DecisionStore()
        self.fallback=HeuristicPolicy()
        if DECISION_POLICY=="llm":
            from ea.llm_policy import LLMPolicy
            self.policy=LLMPolicy(OPENAI_API_KEY,OPENAI_MODEL)
        else:
            self.policy=self.fallback

    def sources(self):
        if DEMO_MODE:return [DemoSource()]
        from ea.connectors.google import GmailSource,CalendarSource
        from ea.connectors.slack import SlackSource
        return [
            GmailSource(GOOGLE_CLIENT_SECRET_FILE,GOOGLE_TOKEN_FILE),
            CalendarSource(GOOGLE_CLIENT_SECRET_FILE,GOOGLE_TOKEN_FILE),
            SlackSource(SLACK_BOT_TOKEN,SLACK_CHANNEL_IDS),
        ]

    def queue(self,include_resolved=False):
        company,user=self.ctx.company(),self.ctx.user()
        resolved=self.store.resolved_ids()
        items=[]
        for source in self.sources():
            try:items.extend(source.fetch(10))
            except Exception as exc:print(f"[EA] Source failed: {exc}")
        items=[i for i in items if include_resolved or i.event_id not in resolved]
        if not items:return []

        out=[]
        with ThreadPoolExecutor(max_workers=min(6,len(items))) as pool:
            futures={pool.submit(self._decide,i,company,user):i for i in items}
            for f in as_completed(futures):
                item=futures[f]
                try:decision=f.result()
                except Exception as exc:
                    print(f"[EA] Unexpected decision failure for {item.event_id}: {exc}")
                    decision=self._fallback(item,company,user)
                out.append((item,decision))
        return sorted(out,key=lambda x:x[0].timestamp,reverse=True)

    def _fallback(self,item,company,user):
        d=self.fallback.decide(item,company,user,SHADOW_MODE)
        d.agent_version="heuristic-fallback-v1"
        return d

    def _decide(self,item,company,user):
        protection=protect_text(item.body)
        if protection.get("status")=="failed":
            return Decision(
                event_id=item.event_id,priority="high",action=Action.ASK,
                summary="Guardrail review required",
                rationale="Future AGI Protect flagged the input before model processing.",
                confidence=.99,risk=.90,
                autonomy_mode=choose_autonomy_mode(.99,.90,SHADOW_MODE),
                agent_version="protect-gated",
            )
        try:return self.policy.decide(item,company,user,SHADOW_MODE)
        except Exception as exc:
            print(f"[EA] Decision failed for {item.event_id}: {exc}")
            return self._fallback(item,company,user)
