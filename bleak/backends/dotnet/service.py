import logging
import asyncio

from asyncio import AbstractEventLoop
from typing import List, Union

# working to implement this


from bleak.backends.service import BleakGATTService
from bleak.backends.dotnet.characteristic import BleakGATTCharacteristicDotNet

from bleak.backends.dotnet.utils import (
    wrap_Task,
    wrap_IAsyncOperation,
    IAsyncOperationAwaitable,
)

from System import Array, Byte, UInt64, Guid
from Windows.Foundation import IAsyncOperation, TypedEventHandler
from Windows.Devices.Bluetooth.GenericAttributeProfile import (
    GattServiceProviderResult,
    GattServiceProvider,
    GattLocalService,
    GattDeviceService
)

logger = logging.getLogger(name=__name__)


class BleakGATTServiceDotNet(BleakGATTService):
    """GATT Characteristic implementation for the .NET backend"""

    def __init__(self, obj: Union[GattDeviceService, GattLocalService]):
        super().__init__(obj)
        self.__characteristics = [
            # BleakGATTCharacteristicDotNet(c) for c in obj.GetAllCharacteristics()
        ]

    @staticmethod
    async def new(_uuid: str, loop: AbstractEventLoop = None) -> BleakGATTService:
        guid = Guid.Parse(_uuid)
        loop = loop if loop is not None else asyncio.get_event_loop()
        spr = await wrap_IAsyncOperation(IAsyncOperation[GattServiceProviderResult](
                GattServiceProvider.CreateAsync(guid)
                ), return_type=GattServiceProviderResult, loop = loop)
        newService = spr.ServiceProvider.Service
        return BleakGATTServiceDotNet(obj=newService)
    
    @property
    def uuid(self):
        return self.obj.Uuid.ToString()

    @property
    def characteristics(self) -> List[BleakGATTCharacteristicDotNet]:
        """List of characteristics for this service"""
        return self.__characteristics

    def get_characteristic(self, _uuid) -> Union[BleakGATTCharacteristicDotNet, None]:
        """Get a characteristic by UUID"""
        try:
            return next(filter(lambda x: x.uuid == _uuid, self.characteristics))
        except StopIteration:
            return None

    def add_characteristic(self, characteristic: BleakGATTCharacteristicDotNet):
        """Add a :py:class:`~BleakGATTCharacteristicDotNet` to the service.

        Should not be used by end user, but rather by `bleak` itself.
        """
        self.__characteristics.append(characteristic)
