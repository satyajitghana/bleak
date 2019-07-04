
"""
Perform Bluetooth LE Scan.

macOS

Created on 2019-06-24 by kevincar <kevincarrolldavis@gmail.com>

"""

import asyncio
from asyncio.events import AbstractEventLoop
from typing import List

from bleak.backends.corebluetooth import CBAPP as cbapp
from bleak.backends.device import BLEDevice

from ..corebluetooth.client import BleakClientCoreBluetooth as BleakClient

from bleak.exc import BleakError


async def discover(
        timeout: float = 5.0,
        loop: AbstractEventLoop = None,
        **kwargs) -> List[BLEDevice]:
    """Perform a Bluetooth LE Scan.

    Args:
        timeout (float): duration of scaning period
        loop (Event Loop): Event Loop to use

    """
    loop = loop if loop else asyncio.get_event_loop()

    client = BleakClient(None, loop)
    await client.is_ready()

    if not client.app.central_manager_delegate.enabled:
        raise BleakError("Bluetooth device is turned off")

    # CoreBluetooth doesn't explicitly use MAC addresses to identify peripheral
    # devices because private devices may obscure their MAC addresses. To cope
    # with this, CoreBluetooth utilizes UUIDs for each peripheral. We'll use
    # this for the BLEDevice address on macOS

    return await client.scan_for_devices(timeout=timeout)
