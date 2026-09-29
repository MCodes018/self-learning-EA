import json
import requests
from ea.config import DATA_DIR, OPENAI_API_KEY, FUTUREAGI_OPT_MODEL

def build_dataset(records):
    return [
        {
            "context": json.dumps({
                "source":r.event.source.value,
                "title":r.event.title,
                "body":r.event.body,
                "sender":r.event.sender,
                "user_context":r.context_snapshot.get("user",{}),
                "company_context":r.context_snapshot.get("company",{}),
            },ensure_ascii=False),
            "expected_action":r.user_action.value,
        }
        for r in records if r.user_action is not None
    ]

class RequestsGenerator:
    """agent-opt compatible generator that avoids the blocked OpenAI/jiter SDK."""
    def __init__(self, model, prompt_template):
        self.model=model; self.prompt_template=prompt_template
    @property
    def model_name(self): return self.model
    def get_prompt_template(self): return self.prompt_template
    def set_prompt_template(self,template): self.prompt_template=template
    def generate(self,prompt_vars,**kwargs):
        prompt=self.prompt_template.format(**prompt_vars)
        body={"model":self.model,"messages":[{"role":"user","content":prompt}]}
        if kwargs.get("response_format"): body["response_format"]=kwargs["response_format"]
        r=requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization":f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"},
            json=body,timeout=60,
        )
        if r.status_code>=400: raise RuntimeError(f"Optimizer model HTTP {r.status_code}: {r.text[:400]}")
        return r.json()["choices"][0]["message"]["content"] or ""

def run_optimization(records):
    dataset=build_dataset(records)
    if len(dataset)<3:
        return {"ok":False,"message":"Need at least 3 resolved decisions with a human-selected action."}
    try:
        from fi.opt.base.evaluator import Evaluator
        from fi.opt.datamappers import BasicDataMapper
        import fi.opt.optimizers.metaprompt as metaprompt_module
        from fi.opt.optimizers.metaprompt import MetaPromptOptimizer
    except Exception as exc:
        return {"ok":False,"message":f"Future AGI agent-opt is unavailable: {exc}"}

    # agent-opt 0.0.1 hardcodes LiteLLMGenerator while scoring. Patch only its
    # transport class so the Future AGI optimizer algorithm still runs without jiter.
    metaprompt_module.LiteLLMGenerator=RequestsGenerator

    evaluator=Evaluator(eval_template="accuracy",eval_model_name="turing_flash")
    mapper=BasicDataMapper(key_map={"input":"context","output":"generated_output","expected":"expected_action"})
    teacher=RequestsGenerator(FUTUREAGI_OPT_MODEL,"{prompt}")
    optimizer=MetaPromptOptimizer(teacher_generator=teacher)

    initial="""Given this executive-assistant context:
{context}
Choose exactly one action from: reply, schedule, delegate, prioritize, archive, ask.
Output only the action."""
    try:
        result=optimizer.optimize(
            evaluator=evaluator,data_mapper=mapper,dataset=dataset,
            initial_prompts=[initial],
            task_description="Predict the executive user's preferred action from context. Output exactly one allowed action. Preserve the {context} placeholder.",
            num_rounds=2,eval_subset_size=min(len(dataset),8),
        )
        best=result.best_generator.get_prompt_template()
        candidate=DATA_DIR/"candidate_action_prompt.txt"
        candidate.write_text(best,encoding="utf-8")
        return {
            "ok":True,"final_score":float(result.final_score),
            "best_prompt":best,"examples":len(dataset),
            "candidate_path":str(candidate),
        }
    except Exception as exc:
        return {"ok":False,"message":f"Future AGI optimization failed: {exc}"}

def promote_candidate():
    candidate=DATA_DIR/"candidate_action_prompt.txt"
    if not candidate.exists():
        return {"ok":False,"message":"No candidate prompt exists yet."}
    active=DATA_DIR/"optimized_action_prompt.txt"
    active.write_text(candidate.read_text(encoding="utf-8"),encoding="utf-8")
    return {"ok":True,"message":"Candidate promoted. New EA decisions will use V2 guidance."}

def active_version():
    return "V2" if (DATA_DIR/"optimized_action_prompt.txt").exists() else "V1"
