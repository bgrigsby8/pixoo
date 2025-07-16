import asyncio
from viam.module.module import Module
try:
    from models.meeting_director import MeetingDirector
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.meeting_director import MeetingDirector


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
