import json
from ea.config import DATA_DIR
from ea.models import DecisionRecord
class DecisionStore:
 def __init__(self):self.path=DATA_DIR/'decisions.jsonl'
 def append(self,r:DecisionRecord):
  with self.path.open('a',encoding='utf-8') as f:f.write(r.model_dump_json()+'\n')
 def all(self):
  if not self.path.exists():return []
  return [DecisionRecord.model_validate(json.loads(x)) for x in self.path.read_text(encoding='utf-8').splitlines() if x.strip()]
 def resolved_ids(self):return {x.event.event_id for x in self.all()}
 def metrics(self):
  r=self.all();n=len(r);a=sum(x.accepted for x in r)
  return {'count':n,'acceptance_rate':a/n if n else 0.0,'correction_rate':(n-a)/n if n else 0.0}
