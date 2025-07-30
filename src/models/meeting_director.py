from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence, Tuple

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

from pixoo import Pixoo
from .google_calendar_service import GoogleCalendarService
from .pixoo_utils import PixooPathDrawer


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

        self.calendar_service = GoogleCalendarService()
        self.google_events = self.calendar_service.get_upcoming_events()

        self.path_emails: Dict[str, str] = attributes["path_emails"]

        self.pixoo = Pixoo(attributes["pixoo_ip"], 64)
        self.pixoo.clear()
        self.pixoo.set_brightness(100)
        
        self.path_drawer = PixooPathDrawer(self.pixoo)

        self.displayed = False
        self.previous_closest_face = None

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
            self.displayed = False
            return {"faces_detected": False}
        
        closest_face = None
        closest_face_area = 0
        for face in faces:
            if face.class_name in self.path_emails.keys():
                self.logger.debug(f"Recognized face: {face.class_name}")
                face_area = (face.x_max - face.x_min) * (face.y_max - face.y_min)
                closest_face = face.class_name if closest_face_area < face_area else closest_face
                closest_face_area = max(closest_face_area, face_area)
            else:
                self.logger.debug("Face not recognized, clearing Pixoo display")
        
        if closest_face:
            if self.previous_closest_face != None and self.previous_closest_face != closest_face:
                self.logger.debug(f"New face detected: {closest_face}, updating Pixoo display")
                self.pixoo.clear()
                self.displayed = False
            self.previous_closest_face = closest_face
            closest_face_email = self.path_emails[closest_face]
            if not self.displayed:
                self._display_user_meeting_directions(closest_face_email)
        else:
            self.logger.debug("No known face detected, clearing Pixoo display")
            self._clear_display()
        
        return {"faces_detected": bool(closest_face), "closest_face": closest_face}

    def _display_user_meeting_directions(self, user_email: str) -> None:
        location = self.calendar_service.find_user_next_meeting(self.google_events, user_email)
        self.logger.debug(f"Next meeting location for {user_email}: {location}")
        if location:
            self.logger.debug(f"Drawing path for {user_email} to {location}")
            self.path_drawer.draw_room_path(location)
            self.displayed = True
        else:
            self._clear_display()

    def _clear_display(self) -> None:
        self.displayed = False
        self.previous_closest_face = None
        self.pixoo.clear()
        self.pixoo.push()

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

