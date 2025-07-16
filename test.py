import asyncio
from pixoo import Pixoo

from viam.robot.client import RobotClient
from viam.components.camera import Camera
from viam.services.vision import VisionClient

async def connect():
    opts = RobotClient.Options.with_api_key( 
        api_key='29jo4duchh7qv4bbqmp37d02gmddrkql',
        api_key_id='47c4fc49-a4bc-4ab2-a8f8-49b47643ce9e'
    )
    return await RobotClient.at_address('pixoo-1-main.8l4pdya4yy.viam.cloud', opts)

async def main():
    machine = await connect()

    # face-identifier
    face_identifier = VisionClient.from_robot(machine, "face-identifier")
    face_identifier_return_value = await face_identifier.get_properties()
    print(f"face-identifier get_properties return value: {face_identifier_return_value}")

    pixoo = Pixoo('10.1.14.195', 64)

    pixoo.fill((0, 0, 255))

    pixoo.push()

    # Don't forget to close the machine when you're done!
    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())
