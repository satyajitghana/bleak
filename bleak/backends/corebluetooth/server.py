"""
BleakServer for CoreBluetooth

Created on 2019-07-03 by kevincar <kevincarrolldavis@gmail.com>
"""

import logging

from typing import Any
from asyncio.events import AbstractEventLoop

from bleak.exc import BleakError
from bleak.backends.server import BaseBleakServer
from bleak.backends.service import BleakGATTServiceCollection, BleakGATTService
from bleak.backends.corebluetooth import Application

logger = logging.getLogger(name=__name__)


class BleakServerCoreBluetooth(BaseBleakServer):
    """CoreBluetooth Implementation of BleakServer"""

    def __init__(self, name: str, loop: AbstractEventLoop, **kwargs):
        super(BleakServerCoreBluetooth, self).__init__(loop=loop, **kwargs)

        self.app = Application(client=False)
        self.name = name
        self.services = BleakGATTServiceCollection()

    async def is_ready(self):
        await self.app._is_delegate_ready()
        logger.debug("BleakServer is ready")

    async def start(self):
        await self.is_ready()
        advertisement_data = {
            "kCBAdvDataServiceUUIDs": list(map(lambda x: x.obj.UUID(), self.services)),
            "kCBAdvDataLocalName": self.name
            }
        logger.debug("Advertisement Data: {}".format(advertisement_data))
        await self.app.peripheral_manager_delegate.startAdvertising_(advertisement_data)
        logger.debug("Advertising...")

    async def stop(self):
        await self.app.peripheral_manager_delegate.stopAdvertising()

    async def add_service(self, service: BleakGATTService):
        """
        Add a service to be advertised
        """
        logger.debug("Adding service {} to server".format(service.uuid))
        if not await self.app.peripheral_manager_delegate.addService_(service.obj):
            raise BleakError("Failed to add Service")
