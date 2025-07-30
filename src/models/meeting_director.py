from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple)

from typing_extensions import Self
from viam.components.camera import Camera
from viam.components.sensor import *
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.services.vision import Vision
from viam.utils import SensorReading, ValueTypes, struct_to_dict

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os.path
import pickle
from pixoo import Pixoo

ARROW_COLOR = (255, 255, 255)
IGNORE_CALENDARS = [
    "Zoom Rooms",
    "Birthdays",
    "Holidays in United States",
    "Tasks"
]
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
PATHS = {
    "NYC Office-6-A1-ELIOT (2) [Zoom Room]": [
        (55, 27),
        (55, 23),
        (5, 23),
    ],
    "NYC Office-6-B4 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-B5 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-B7 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-B8 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-C5 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-C8 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-D4 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-D8 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-E4 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-E7 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-F1 (6) [Zoom Room]": [
        (55, 27),
        (55, 23),
        (12, 23),
    ],
    "NYC Office-6-F2 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-F3 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-F4 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-F5 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-F12 (24) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-H1 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-L8 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-L9 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-L10 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-M2 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-Q2 (6) [Zoom Room]": [
        ()
    ],
    "NYC Office-6-Q6 (6) [Zoom Room]": [
        ()
    ], 
    "NYC Office-6-R2 (4) [Zoom Room]": [
        ()
    ], 
    "NYC Office-6-R6 (6) [Zoom Room]": [
        ()
    ],                                    
    "NYC Office-6-W1 (12) [Zoom Room]": [
        (55, 27),
        (55, 25),
        (59, 25),
        (59, 24),
    ],
    "NYC Office-6-V8 (6) [Zoom Room]": [
        (55, 29),
        (55, 32),
    ],
    "NYC Office-6-W8 (6) [Zoom Room]": [
        (55, 29),
        (55, 30),
        (57, 30),
        (57, 32),
    ],
    "NYC Office-6-X8 (6) [Zoom Room]": [
        (55, 29),
        (55, 30),
        (60, 30),
        (60, 32),
    ]
}


def send_right_arrow(pixoo: Pixoo):
    pixoo.draw_filled_rectangle((15, 32), (40, 40), ARROW_COLOR)
    for i in range(13):
        x   = 41 + i      
        y1  = 24 + i          
        y2  = 48 - i    
        pixoo.draw_line((x, y1), (x, y2), ARROW_COLOR)
    pixoo.push()

def send_left_arrow(pixoo: Pixoo):
    pixoo.draw_filled_rectangle((23, 34), (48, 42), ARROW_COLOR)
    for i in range(13):
        x   = 22 - i
        y1  = 26 + i  
        y2  = 50 - i
        pixoo.draw_line((x, y1), (x, y2), ARROW_COLOR)
    pixoo.push()

def send_up_arrow(pixoo: Pixoo):
    pixoo.draw_filled_rectangle((28, 39), (36, 54), ARROW_COLOR)
    for i in range(13):
        y   = 38 - i      
        x1  = 20 + i     
        x2  = 44 - i     
        pixoo.draw_line((x1, y), (x2, y), ARROW_COLOR)
    pixoo.push()

def send_down_arrow(pixoo: Pixoo):
    pixoo.draw_filled_rectangle((28, 25), (36, 40), ARROW_COLOR)
    for i in range(13):
        y   = 41 + i       
        x1  = 20 + i        
        x2  = 44 - i        
        pixoo.draw_line((x1, y), (x2, y), ARROW_COLOR)
    pixoo.push()

def get_google_credentials():
    creds = None
    if os.path.exists('/home/pixoo/pixoo/token.pickle'):
        with open('/home/pixoo/pixoo/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # if not creds or not creds.valid:
    #     flow = InstalledAppFlow.from_client_secrets_file('/home/pixoo/pixoo/credentials.json', SCOPES)
    #     creds = flow.run_local_server(port=0)
    #     with open('/home/pixoo/pixoo/token.pickle', 'wb') as token:
    #         pickle.dump(creds, token)
    return creds

def get_google_events():
    creds = get_google_credentials()
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    end = (datetime.datetime.utcnow() + datetime.timedelta(minutes=1560)).isoformat() + 'Z' 

    calendar_list = service.calendarList().list().execute()

    for calendar in calendar_list['items']:
        cal_id = calendar['id']

        events = service.events().list(
            calendarId=cal_id,
            timeMin=now,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        if events['summary'] in IGNORE_CALENDARS:
            continue

        return events

def something(events, email):
    for event in events.get('items', []):
        attendees = event.get('attendees', [])
        for attendee in attendees:
            if attendee.get('email') == email:
                location = event.get('location')
                draw_pixoo(location)
                return

def draw_pixoo(location):
    pixoo = Pixoo()

    for path_point in range(len(PATHS[location]) - 1):
        pixoo.draw_line(PATHS[location][path_point], PATHS[location][path_point + 1], (255, 255, 255))
    pixoo.push()

class MeetingDirector(Sensor, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(
        ModelFamily("brad-grigsby", "pixoo"), "meeting-director"
    )

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        return super().new(config, dependencies)

    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        attributes = struct_to_dict(config.attributes)

        if "camera_name" not in attributes:
            raise ValueError("Missing required attribute 'camera_name' in config")
        camera_name = attributes["camera_name"]

        if "pixoo_ip" not in attributes:
            raise ValueError("Missing required attribute 'pixoo_ip' in config")

        if "face_detector" not in attributes:
            raise ValueError("Missing required attribute 'face_detector' in config")
        face_detector_name = attributes["face_detector"]

        if "path_emails" not in attributes:
            raise ValueError("Missing required attribute 'path_emails' in config")

        return [camera_name, face_detector_name], []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        attributes = struct_to_dict(config.attributes)

        self.camera: Camera = dependencies[Camera.get_resource_name(attributes["camera_name"])]
        self.face_detector: Vision = dependencies[Vision.get_resource_name(attributes["face_detector"])]

        # Collect all google events
        self.google_events = get_google_events()
        self.logger.debug("Google events collected: %s", self.google_events)

        # Name path to emails
        self.path_emails: Dict[str, str] = attributes["path_emails"]

        # Setup pixoo display
        self.pixoo = Pixoo(attributes["pixoo_ip"], 64)
        self.pixoo.clear()
        self.pixoo.set_brightness(100)

        return super().reconfigure(config, dependencies)

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        # Capture an image from the camera
        viam_image = await self.camera.get_image()

        # Run face detection
        faces = await self.face_detector.get_detections(viam_image)
        if not faces:
            self.pixoo.clear()
            self.pixoo.push()
            return {"faces_detected": False}
        
        closest_face = None
        closest_face_area = 0
        for face in faces:
            if face.class_name in self.path_emails.keys():
                face_area = (face.x_max - face.x_min) * (face.y_max - face.y_min)
                closest_face = face.class_name if closest_face_area < face_area else closest_face
                closest_face_area = max(closest_face_area, face_area)
            else:
                self.logger.debug("Face not recognized, clearing Pixoo display")
        
        if closest_face:
            closest_face_email = self.path_emails[closest_face]
            something(self.google_events, closest_face_email)
        else:
            self.logger.debug("No known face detected, clearing Pixoo display")
            self.pixoo.clear()
            self.pixoo.push()
        
        return {"faces_detected": bool(closest_face), "closest_face": closest_face}


    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        self.logger.error("`do_command` is not implemented")
        raise NotImplementedError()

    async def get_geometries(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
    ) -> List[Geometry]:
        self.logger.error("`get_geometries` is not implemented")
        raise NotImplementedError()

