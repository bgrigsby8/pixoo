from typing import List, Tuple
from pixoo import Pixoo
import pixoo
from .config import (
    ARROW_COLOR, 
    PATH_COLOR,
    ROOM_PATHS
)


class PixooArrowDrawer:
    def __init__(self, pixoo: Pixoo):
        self.pixoo = pixoo

    def draw_right_arrow(self) -> None:
        self.pixoo.draw_filled_rectangle((15, 32), (40, 40), ARROW_COLOR)
        for i in range(13):
            x = 41 + i
            y1 = 24 + i
            y2 = 48 - i
            self.pixoo.draw_line((x, y1), (x, y2), ARROW_COLOR)
        self.pixoo.push()

    def draw_left_arrow(self) -> None:
        self.pixoo.draw_filled_rectangle((23, 34), (48, 42), ARROW_COLOR)
        for i in range(13):
            x = 22 - i
            y1 = 26 + i
            y2 = 50 - i
            self.pixoo.draw_line((x, y1), (x, y2), ARROW_COLOR)
        self.pixoo.push()

    def draw_up_arrow(self) -> None:
        self.pixoo.draw_filled_rectangle((28, 39), (36, 54), ARROW_COLOR)
        for i in range(13):
            y = 38 - i
            x1 = 20 + i
            x2 = 44 - i
            self.pixoo.draw_line((x1, y), (x2, y), ARROW_COLOR)
        self.pixoo.push()

    def draw_down_arrow(self) -> None:
        self.pixoo.draw_filled_rectangle((28, 25), (36, 40), ARROW_COLOR)
        for i in range(13):
            y = 41 + i
            x1 = 20 + i
            x2 = 44 - i
            self.pixoo.draw_line((x1, y), (x2, y), ARROW_COLOR)
        self.pixoo.push()


class PixooPathDrawer:
    def __init__(self, pixoo: Pixoo):
        self.pixoo = pixoo

    def draw_room_path(self, location: str) -> None:
        if location not in ROOM_PATHS:
            return
        
        # Draw office map
        self.pixoo.draw_line((2, 22), (62, 22), ARROW_COLOR)
        self.pixoo.draw_line((62, 22), (62, 34), ARROW_COLOR)
        self.pixoo.draw_line((62, 34), (46, 34), ARROW_COLOR)
        self.pixoo.draw_line((46, 34), (30, 63), ARROW_COLOR)
        self.pixoo.draw_line((30, 63), (15, 63), ARROW_COLOR)
        self.pixoo.draw_line((15, 63), (2, 22), ARROW_COLOR)

        # Draw current location
        self.pixoo.draw_pixel((55, 28), (255, 0, 0))
        self.pixoo.push()
        
        path_points = ROOM_PATHS[location]
        if len(path_points) < 2:
            return
            
        for i in range(len(path_points) - 1):
            self.pixoo.draw_line(
                path_points[i], 
                path_points[i + 1], 
                PATH_COLOR
            )
        self.pixoo.draw_text(location, (2, 3), (255, 255, 255))
        self.pixoo.push()

        # self.pixoo.send_text(location, (24, 0), (255, 255, 255), 1, 3)