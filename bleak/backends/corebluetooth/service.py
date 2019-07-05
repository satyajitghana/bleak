import logging

from typing import List, Union

from bleak.backends.service import BleakGATTService
from bleak.backends.corebluetooth.characteristic import BleakGATTCharacteristicCoreBluetooth

from Foundation import CBService, CBMutableService, CBUUID, NSStringFromClass, NSMutableArray

logger = logging.getLogger(name=__name__)


class BleakGATTServiceCoreBluetooth(BleakGATTService):
    """GATT Service implementation for the CoreBluetooth backend"""

    def __init__(self, obj: CBService):
        super().__init__(obj)
        self.__characteristics = []

    @staticmethod
    def new(_uuid: str) -> BleakGATTService:
        cUUID = CBUUID.alloc().initWithString_(_uuid)
        newService = CBMutableService.alloc().initWithType_primary_(cUUID, True)
        logger.debug("New CBMutableService created for {}".format(_uuid))
        return BleakGATTServiceCoreBluetooth(obj=newService)

    @property
    def uuid(self) -> str:
        return self.obj.UUID().UUIDString()

    @property
    def characteristics(self) -> List[BleakGATTCharacteristicCoreBluetooth]:
        """List of characteristics for this service"""
        return self.__characteristics

    def get_characteristic(self, _uuid: CBUUID) -> Union[BleakGATTCharacteristicCoreBluetooth, None]:
        """Get a characteristic by UUID"""
        try:
            return next(filter(lambda x: x.uuid == _uuid, self.characteristics))
        except StopIteration:
            return None


    def add_characteristic(self, characteristic: BleakGATTCharacteristicCoreBluetooth):
        """Add a :py:class:`~BleakGATTCharacteristicDotNet` to the service.

        Should not be used by end user, but rather by `bleak` itself.
        """
        self.__characteristics.append(characteristic)
        
        obj_class_name = NSStringFromClass(self.obj.class__())
        if obj_class_name == "CBMutableService":
            characteristics = list(map(lambda x: x.obj, self.__characteristics))
            self.obj.setCharacteristics_(characteristics)
            logger.debug("Adding CBMutableCharacteristic {} to CBMutableService {}".format(characteristic.uuid, self.uuid))

