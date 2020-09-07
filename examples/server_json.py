import logging
import asyncio
import json

from typing import Any

from bleak.backends.characteristic import GattCharacteristicsFlags
from bleak import BleakServer, BleakGATTCharacteristic

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

ink_service_name = "INK"
ink_service = dict(
    uuid="A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
    )
ink_characteristric = dict(
    service_uuid=ink_service['uuid'],
    char_uuid="51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B",
    properties=GattCharacteristicsFlags.read.value | GattCharacteristicsFlags.write.value |\
         GattCharacteristicsFlags.indicate.value | GattCharacteristicsFlags.notify.value,
    value=None,
    permissions= 0x1 | 0x2
    )

def read_request(characteristic: BleakGATTCharacteristic, **kwargs) -> bytearray:
    """Say Hello to whoever called the read on this characteristic"""
    logger.debug(f"DANG {characteristic.value}")
    return bytearray('Hello From the Ink BLE server !', encoding='utf-8')

def write_request(characteristic: BleakGATTCharacteristic, value: Any, **kwargs):
    """This will set the characteristic value to whatever was received"""
    characteristic.set_value(value)
    logger.debug(f"Char value set to {characteristic.value}")

async def run(loop):
    server = BleakServer(name=ink_service_name, loop=loop)
    await server.add_new_service(ink_service['uuid'])
    print(ink_characteristric)
    await server.add_new_characteristic(**ink_characteristric)

    server.read_request_func = read_request
    server.write_request_func = write_request

    await server.start()
    logger.info('=> BLE GATT Server Started !')
    await asyncio.sleep(10)

    with open('test.json') as f:
        json_data = json.load(f)

        for data in json_data:
            print(data)
            server.services.get_characteristic(ink_characteristric['char_uuid']).set_value(bytearray(str(data), encoding='utf-8'))
            server.updateValue(ink_service['uuid'], ink_characteristric['char_uuid'])
            await asyncio.sleep(2)

    logger.info('=> Stopping . . .')
    await server.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
