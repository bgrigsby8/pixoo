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
KNOWN_FACES = ["brad"]
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


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

def get_google_calendars():
    creds = get_google_credentials()
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    end = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + 'Z'  # next 24 hours

    calendar_list = service.calendarList().list().execute()

    emails = []
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

        for event in events.get('items', []):
            attendees = event.get('attendees', [])
            for attendee in attendees:
                emails.append(attendee['email'])
            break
        break

    return emails


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

        return [camera_name, face_detector_name], []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        attributes = struct_to_dict(config.attributes)

        self.camera: Camera = dependencies[Camera.get_resource_name(attributes["camera_name"])]
        self.face_detector: Vision = dependencies[Vision.get_resource_name(attributes["face_detector"])]

        # Collect all google emails
        self.google_emails = get_google_calendars()
        self.logger.debug("Google emails collected: %s", self.google_emails)

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
            if face.class_name in KNOWN_FACES:
                face_area = (face.x_max - face.x_min) * (face.y_max - face.y_min)
                closest_face = face.class_name if closest_face_area < face_area else closest_face
                closest_face_area = max(closest_face_area, face_area)
            else:
                self.logger.debug("Face not recognized, clearing Pixoo display")
        
        if closest_face:
            # Display the arrow pattern on the Pixoo
            send_left_arrow(self.pixoo)
            self.pixoo.send_text('A2', (24, 3), (255, 255, 255), 1, 7)
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

