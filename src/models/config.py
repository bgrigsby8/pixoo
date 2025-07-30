from typing import List, Dict, Tuple

ARROW_COLOR = (255, 255, 255)
PATH_COLOR = (0, 255, 0)

IGNORE_CALENDARS = [
    "Zoom Rooms",
    "Birthdays",
    "Holidays in United States",
    "Tasks"
]

GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

ROOM_PATHS: Dict[str, List[Tuple[int, int]]] = {
    "NYC Office-6-A1-ELIOT (2) [Zoom Room]": [
        (55, 27),
        (55, 23),
        (5, 23),
    ],
    "NYC Office-6-B4 (6) [Zoom Room]": [],
    "NYC Office-6-B5 (6) [Zoom Room]": [],
    "NYC Office-6-B7 (6) [Zoom Room]": [],
    "NYC Office-6-B8 (6) [Zoom Room]": [],
    "NYC Office-6-C5 (6) [Zoom Room]": [],
    "NYC Office-6-C8 (6) [Zoom Room]": [],
    "NYC Office-6-D4 (6) [Zoom Room]": [],
    "NYC Office-6-D8 (6) [Zoom Room]": [],
    "NYC Office-6-E4 (6) [Zoom Room]": [],
    "NYC Office-6-E7 (6) [Zoom Room]": [],
    "NYC Office-6-F1 (6) [Zoom Room]": [
        (55, 27),
        (55, 23),
        (12, 23),
    ],
    "NYC Office-6-F2 (6) [Zoom Room]": [],
    "NYC Office-6-F3 (6) [Zoom Room]": [],
    "NYC Office-6-F4 (6) [Zoom Room]": [],
    "NYC Office-6-F5 (6) [Zoom Room]": [],
    "NYC Office-6-F12 (24) [Zoom Room]": [],
    "NYC Office-6-H1 (6) [Zoom Room]": [],
    "NYC Office-6-L8 (6) [Zoom Room]": [],
    "NYC Office-6-L9 (6) [Zoom Room]": [],
    "NYC Office-6-L10 (6) [Zoom Room]": [],
    "NYC Office-6-M2 (6) [Zoom Room]": [],
    "NYC Office-6-Q2 (6) [Zoom Room]": [],
    "NYC Office-6-Q6 (6) [Zoom Room]": [],
    "NYC Office-6-R2 (4) [Zoom Room]": [],
    "NYC Office-6-R6 (6) [Zoom Room]": [],
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

PIXOO_FILE_PATHS = {
    "token": "/home/pixoo/pixoo/token.pickle",
    "credentials": "/home/pixoo/pixoo/credentials.json"
}