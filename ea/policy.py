from ea.models import Action,Decision,Source
from ea.autonomy import choose_autonomy_mode
class HeuristicPolicy:
 def decide(self,item,company,user,shadow):
  t=(item.title+' '+item.body).lower()
  if any(x in t for x in ('enterprise','partnership','urgent','customer')):a,p,c,r,s,w=Action.PRIORITIZE,'high',.84,.18,'Important business request','Matches current business-priority signals.'
  elif item.source==Source.CALENDAR or any(x in t for x in ('meeting','schedule','call')):a,p,c,r,s,w=Action.SCHEDULE,'medium',.80,.15,'Scheduling request','Calendar context should be checked.'
  elif item.source==Source.SLACK:a,p,c,r,s,w=Action.PRIORITIZE,'medium',.72,.10,'Internal request','Internal request surfaced for calibration.'
  elif 'newsletter' in t or 'unsubscribe' in t:a,p,c,r,s,w=Action.ARCHIVE,'low',.94,.05,'Low-value information','Looks like a newsletter.'
  else:a,p,c,r,s,w=Action.ASK,'medium',.55,.10,'Needs judgment','Insufficient evidence.'
  return Decision(event_id=item.event_id,priority=p,action=a,summary=s,rationale=w,confidence=c,risk=r,autonomy_mode=choose_autonomy_mode(c,r,shadow),agent_version='heuristic-v1')
