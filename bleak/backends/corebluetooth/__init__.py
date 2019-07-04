# -*- coding: utf-8 -*-
"""
__init__.py

Created on 2017-11-19 by hbldh <henrik.blidh@nedomkull.com>

"""

# Use PyObjC and PyObjC Core Bluetooth bindings for Bleak!
import asyncio
from Foundation import NSDate, NSDefaultRunLoopMode, NSRunLoop
from .CentralManagerDelegate import CentralManagerDelegate
from .PeripheralManagerDelegate import PeripheralManagerDelegate

# async def discover(device="hci0", timeout=5.0):
    # raise NotImplementedError("CoreBluetooth discover not implemented yet.")

class Application():
    """
    This is a temporary application class responsible for running the NSRunLoop
    so that events within CoreBluetooth are appropriately handled
    """

    ns_run_loop_done = False
    ns_run_loop_interval = 0.001

    def __init__(self, client: bool = True):
        self.main_loop = asyncio.get_event_loop()
        self.main_loop.create_task(self._handle_nsrunloop())
        self.main_loop.create_task(self._is_delegate_ready())

        self.nsrunloop = NSRunLoop.currentRunLoop()
        
        self.central_manager_delegate = CentralManagerDelegate.alloc().init() if client else None
        self.peripheral_manager_delegate = PeripheralManagerDelegate.alloc().init() if not client else None

    def __del__(self):
        self.ns_run_loop_done = True

    async def _handle_nsrunloop(self):
        while not self.ns_run_loop_done:
            time_interval = NSDate.alloc().initWithTimeIntervalSinceNow_(self.ns_run_loop_interval)
            self.nsrunloop.runMode_beforeDate_(NSDefaultRunLoopMode, time_interval)
            await asyncio.sleep(0)

    async def _is_delegate_ready(self):
        if self.central_manager_delegate is not None:
            await self.central_manager_delegate.is_ready()
        else:
            await self.peripheral_manager_delegate.is_ready()
