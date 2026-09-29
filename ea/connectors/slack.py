from datetime import datetime,timezone
from slack_sdk import WebClient
from ea.models import WorkItem,Source
class SlackSource:
 def __init__(self,token,channels):
  if not token or not channels:raise ValueError('Configure SLACK_BOT_TOKEN and SLACK_CHANNEL_IDS.')
  self.c=WebClient(token=token);self.channels=channels
 def fetch(self,limit=10):
  out=[]
  for ch in self.channels:
   for m in self.c.conversations_history(channel=ch,limit=max(1,limit//len(self.channels))).get('messages',[]):out.append(WorkItem(event_id=f"slack-{ch}-{m['ts']}",source=Source.SLACK,sender=m.get('user','Slack user'),title=f'Slack #{ch}',body=m.get('text',''),timestamp=datetime.fromtimestamp(float(m['ts']),tz=timezone.utc)))
  return sorted(out,key=lambda x:x.timestamp,reverse=True)[:limit]
