"""
PeripheralManagerDelegate file. This class will function as the delegate
NSObject for the CBPeripheralManager object used by CoreBluetooth advertising
servers

Created on 2019-07-03 by kevincar <kevincarrolldavis@gmail.com>
"""

import objc
import logging
import asyncio

from typing import Any

from bleak.exc import BleakError

from Foundation import NSObject, \
    CBPeripheralManager, \
    CBCentral, \
    CBMutableService, \
    CBService, \
    CBCharacteristic, \
    CBATTRequest, \
    NSError


CBPeripheralManagerDelegate = objc.protocolNamed("CBPeripheralManagerDelegate")

logger = logging.getLogger(name=__name__)


class PeripheralManagerDelegate(NSObject):
    """
    This class will conform to the CBPeripheralManagerDelegate protocol to
    manage messages passed from the owning PeripheralManager class
    """
    ___pyobjc_protocols__ = [CBPeripheralManagerDelegate]

    def init(self):
        """macOS init function for NSObjects"""
        self = objc.super(PeripheralManagerDelegate, self).init()

        self.peripheral_manager = CBPeripheralManager.alloc().initWithDelegate_queue_(self, None)

        self.ready = False

        self._services_added_log = {}
        self._services_added_result = {}
        self._advertisement_started = False

        self._central_subscriptions = {}

        return self

    # User-defined functions

    async def is_ready(self) -> bool:
        """Wait for ready state of the peripheralManager"""
        while not self.ready:
            await asyncio.sleep(0.01)

        return True

    async def addService_(self, service: CBMutableService) -> bool:
        """Add service to the peripheral"""
        UUID = service.UUID().UUIDString()
        self._services_added_log[UUID] = False
    
        self.peripheral_manager.addService_(service)

        while not self._services_added_log[UUID]:
            await asyncio.sleep(0.01)

        return self._services_added_result[UUID]

    async def startAdvertising_(self, advertisement_data: [str, Any]):

        self.peripheral_manager.startAdvertising_(advertisement_data)

        while not self._advertisement_started:
            await asyncio.sleep(0.01)

        logger.debug("Advertising started with the following data: {}".format(advertisement_data))

    async def stopAdvertising(self):

        self.peripheral_manager.stopAdvertising()
        await asyncio.sleep(0.01)

    # Protocol-specific functions

    def peripheralManagerDidUpdateState_(self, peripheral: CBPeripheralManager):
        if peripheral.state() == 0:
            logger.debug("Cannot detect bluetooth device")
        elif peripheral.state() == 1:
            logger.debug("Bluetooth is resetting")
        elif peripheral.state() == 2:
            logger.debug("Bluetooth is unsupported")
        elif peripheral.state() == 3:
            logger.debug("Bluetooth is unauthorized")
        elif peripheral.state() == 4:
            logger.debug("Bluetooth powered off")
        elif peripheral.state() == 5:
            logger.debug("Bluetooth powered on")

        self.ready = True

    def peripheralManager_willRestoreState_(self, peripheral: CBPeripheralManager, d: dict):
        logger.debug("PeripheralManager restoring state: {}".format(d))

    def peripheralManager_didAddService_error_(self, peripheral: CBPeripheralManager, service: CBService, error: NSError):
        UUID = service.UUID().UUIDString()
        if error:
            self._services_added_result[UUID] = False
            raise BleakError("Failed to add service {}: {}".format(UUID, error))

        logger.debug("Peripheral manager did add service: {}".format(UUID))
        logger.debug("service added had characteristics: {}".format(service.characteristics()))
        self._services_added_result[UUID] = True
        self._services_added_log[UUID] = True

    def peripheralManagerDidStartAdvertising_error_(self, peripheral: CBPeripheralManager, error: NSError):
        if error:
            raise BleakError("Failed to start advertising: {}".format(error))

        logger.debug("Peripheral manager did start advertising")
        self._advertisement_started = True

    def peripheralManager_central_didSubscribeToCharacteristic_(self, peripheral: CBPeripheralManager, central: CBCentral, characteristic: CBCharacteristic):
        central_uuid = central.identifier().UUIDString()
        char_uuid = characteristic.UUID().UUIDString()
        logger.debug("Central Device: {} is subscribing to characteristic {}".format(central_uuid, char_uuid))
        if self._central_subscriptions[central_uuid]:
            subscriptions = self._central_subscriptions[central_uuid]
            if char_uuid not in subscriptions:
                self._central_subscriptions[central_uuid].append(char_uuid)
            else:
                logger.debug("Central Device {} is already subscribed to characteristic {}".format(central_uuid, char_uuid))
        else:
            self._central_subscriptions[central_uuid] = [char_uuid]
    
    def peripheralManager_central_didUnsubscribeFromCharacteristic_(self, peripheral: CBPeripheralManager, central: CBCentral, characteristic: CBCharacteristic):
        central_uuid = central.identifier().UUIDString()
        char_uuid = characteristic.UUID().UUIDString()
        logger.debug("Central device {} is unsubscribing from characteristic {}".format(central_uuid, char_uuid))
        self._central_subscriptions[central_uuid].remove(char_uuid)

    def peripheralManagerIsReadyToUpdateSubscribers_(self, peripheral: CBPeripheralManager):
        logger.debug("Peripheral is ready to update subscribers")

    def peripheralManager_didReceiveReadRequest_(self, peripheral: CBPeripheralManager, request: CBATTRequest):
        # This should probably be a callback to be handled by the user, to be implemented or given to the BleakServer
        logger.debug("Received read request from {} for characteristic {}".format(request.central().identifier().UUIDString(), request.characteristic().UUID().UUIDString()))
        peripheral.respondToRequest_withResult_(request, CBATTError.Success)

    def peripheralManager_didReceiveWriteRequests_(self, peripheral: CBPeripheralManager, requests: [CBATTRequest]):
        # Again, this should likely be moved to a callback
        logger.debug("Received write requests from {} for charactersitics {}".format(list(map(lambda x: x.central().identifier().UUIDString(), requests)), list(map(lambda x: x.characteristic().UUID().UUIDString(), requests))))
        peripheral.respondToRequest_withResult_(requests[0], CBATTError.Success)