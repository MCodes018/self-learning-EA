from datetime import datetime,timezone
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from ea.models import WorkItem,Source
SCOPES=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.readonly']
def auth(client,token):
 p=Path(token);c=Credentials.from_authorized_user_file(str(p),SCOPES) if p.exists() else None
 if c and c.expired and c.refresh_token:c.refresh(Request())
 elif not c or not c.valid:c=InstalledAppFlow.from_client_secrets_file(client,SCOPES).run_local_server(port=0)
 p.write_text(c.to_json(),encoding='utf-8');return c
class GmailSource:
 def __init__(self,client,token):self.c=auth(client,token)
 def fetch(self,limit=10):
  s=build('gmail','v1',credentials=self.c,cache_discovery=False);rows=s.users().messages().list(userId='me',maxResults=limit,q='in:inbox').execute();out=[]
  for row in rows.get('messages',[]):
   m=s.users().messages().get(userId='me',id=row['id'],format='metadata',metadataHeaders=['From','Subject']).execute();h={x['name'].lower():x['value'] for x in m['payload'].get('headers',[])}
   out.append(WorkItem(event_id='gmail-'+m['id'],source=Source.GMAIL,sender=h.get('from'),title=h.get('subject','(no subject)'),body=m.get('snippet',''),timestamp=datetime.fromtimestamp(int(m['internalDate'])/1000,tz=timezone.utc)))
  return out
class CalendarSource:
 def __init__(self,client,token):self.c=auth(client,token)
 def fetch(self,limit=10):
  s=build('calendar','v3',credentials=self.c,cache_discovery=False);rows=s.events().list(calendarId='primary',timeMin=datetime.now(timezone.utc).isoformat(),maxResults=limit,singleEvents=True,orderBy='startTime').execute()
  return [WorkItem(event_id='cal-'+e['id'],source=Source.CALENDAR,sender=e.get('organizer',{}).get('email'),title=e.get('summary','(untitled)'),body=e.get('description','') or str(e.get('start',{})),timestamp=datetime.now(timezone.utc)) for e in rows.get('items',[])]
