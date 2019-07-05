"""
BleakServer for CoreBluetooth

Created on 2019-07-03 by kevincar <kevincarrolldavis@gmail.com>
"""

import logging

from typing import Any, Callable
from asyncio.events import AbstractEventLoop

from bleak.exc import BleakError
from bleak.backends.server import BaseBleakServer
from bleak.backends.service import BleakGATTServiceCollection, BleakGATTService, BleakGATTCharacteristic
from bleak.backends.corebluetooth import Application

logger = logging.getLogger(name=__name__)


class BleakServerCoreBluetooth(BaseBleakServer):
    """CoreBluetooth Implementation of BleakServer"""

    def __init__(self, name: str, loop: AbstractEventLoop, **kwargs):
        super(BleakServerCoreBluetooth, self).__init__(loop=loop, **kwargs)

        self.app = Application(client=False)
        self.name = name
        self.services = BleakGATTServiceCollection()
        self.read_request_func = None
        self.write_request_func = None

    async def is_ready(self):
        await self.app._is_delegate_ready()
        self.app.peripheral_manager_delegate.readRequestFunc = self.read_request
        self.app.peripheral_manager_delegate.writeRequestsFunc = self.write_request
        logger.debug("BleakServer is ready")

    async def start(self):
        await self.is_ready()
        
        if not self.read_request_func or not self.write_request_func:
            raise BleakError("Callback functions must be initialized first")

        advertisement_data = {
            "kCBAdvDataServiceUUIDs": list(map(lambda x: x.obj.UUID(), self.services)),
            "kCBAdvDataLocalName": self.name
            }
        logger.debug("Advertisement Data: {}".format(advertisement_data))
        await self.app.peripheral_manager_delegate.startAdvertising_(advertisement_data)
        logger.debug("Advertising...")

    async def stop(self):
        await self.app.peripheral_manager_delegate.stopAdvertising()

    def is_connected(self) -> bool:
        """
        Determine whether there are any connected peripheral devices
        """
        n_subscriptions = len(self.app.peripheral_manager_delegate._central_subscriptions)
        return n_subscriptions > 0

    def is_advertising(self) -> bool:
        """
        Determine whether the service is advertising
        """
        return self.app.peripheral_manager_delegate.is_advertising() == 1
    
    async def add_service(self, service: BleakGATTService):
        """
        Add a service and all it's characteristics to be advertised
        """
        logger.debug("Adding service {} to server".format(service.uuid))
        self.services.add_service(service)
        for characteristic in service.characteristics:
            self.services.add_characteristic(characteristic)

        if not await self.app.peripheral_manager_delegate.addService_(service.obj):
            raise BleakError("Failed to add Service")

    def read_request(self, uuid: str) -> bytearray:
        characteristic = self.services.get_characteristic(uuid)
        logger.debug("Char: {}".format(characteristic))
        if not characteristic:
            raise BleakError("Invalid characteristic: {}".format(uuid))

        return self.read_request_func(characteristic, server=self)

    def write_request(self, uuid: str, value: Any):
        logger.debug("Write request for char {} to value: {}".format(uuid, value))
        characteristic = self.services.get_characteristic(uuid)
        self.write_request_func(characteristic, value)
