from typing import Dict, Any, Optional
import datetime
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from .config import GOOGLE_CALENDAR_SCOPES, IGNORE_CALENDARS, PIXOO_FILE_PATHS


class GoogleCalendarService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self._initialize_service()

    def _get_credentials(self) -> Optional[Any]:
        creds = None
        if os.path.exists(PIXOO_FILE_PATHS["token"]):
            with open(PIXOO_FILE_PATHS["token"], 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    PIXOO_FILE_PATHS["credentials"], 
                    GOOGLE_CALENDAR_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(PIXOO_FILE_PATHS["token"], 'wb') as token:
                pickle.dump(creds, token)
        
        return creds

    def _initialize_service(self) -> None:
        self.credentials = self._get_credentials()
        if self.credentials:
            self.service = build('calendar', 'v3', credentials=self.credentials)

    def get_upcoming_events(self, time_window_minutes: int = 5) -> Optional[Dict[str, Any]]:
        if not self.service:
            return None

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        end = (datetime.datetime.utcnow() + datetime.timedelta(minutes=time_window_minutes)).isoformat() + 'Z'

        calendar_list = self.service.calendarList().list().execute()
        all_events = []

        for calendar in calendar_list['items']:
            if calendar.get('summary', '') in IGNORE_CALENDARS:
                continue

            cal_id = calendar['id']
            events = self.service.events().list(
                calendarId=cal_id,
                timeMin=now,
                timeMax=end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            if events.get('items'):
                all_events.extend(events['items'])

        if all_events:
            all_events.sort(key=lambda x: x.get('start', {}).get('dateTime', x.get('start', {}).get('date', '')))
            return {'items': all_events}

        return None

    def find_user_next_meeting(self, events: Dict[str, Any], user_email: str) -> Optional[str]:
        if not events or 'items' not in events:
            return None

        for event in events['items']:
            attendees = event.get('attendees', [])
            for attendee in attendees:
                if attendee.get('email') == user_email:
                    return event.get('location')

        return None