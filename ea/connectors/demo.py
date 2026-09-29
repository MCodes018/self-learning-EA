from datetime import datetime,timedelta,timezone
from ea.models import WorkItem,Source
class DemoSource:
 def fetch(self,limit=10):
  n=datetime.now(timezone.utc)
  return [
   WorkItem(event_id='g1',source=Source.GMAIL,sender='rahul@acme.example',title='Enterprise AI training partnership',body='We are evaluating AI training partners and would like a 30-minute call next week.',timestamp=n-timedelta(minutes=8)),
   WorkItem(event_id='s1',source=Source.SLACK,sender='Operations',title='Cohort venue hold expires today',body='Can you confirm whether we should lock the venue today?',timestamp=n-timedelta(minutes=25)),
   WorkItem(event_id='c1',source=Source.CALENDAR,sender='Calendar',title='Internal weekly sync',body='Proposed for tomorrow at 9:00 AM.',timestamp=n-timedelta(hours=1)),
   WorkItem(event_id='g2',source=Source.GMAIL,sender='newsletter@example.com',title='Weekly AI newsletter',body='This week in AI. Unsubscribe at any time.',timestamp=n-timedelta(hours=2))][:limit]
