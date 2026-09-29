import json
from ea.config import DATA_DIR
class ContextStore:
 def __init__(self,user_id):self.user_id=user_id
 def company(self):return self._read(DATA_DIR/'company_context.json')
 def user(self):return self._read(DATA_DIR/f'{self.user_id}.json')
 @staticmethod
 def _read(p):
  with p.open('r',encoding='utf-8') as f:return json.load(f)
 @staticmethod
 def save_user(uid,data):
  with (DATA_DIR/f'{uid}.json').open('w',encoding='utf-8') as f:json.dump(data,f,indent=2,ensure_ascii=False)
