# -*- coding: utf-8 -*-
"""
__init__.py

Created on 2017-11-19 by hbldh <henrik.blidh@nedomkull.com>

"""

# Use PyObjC and PyObjC Core Bluetooth bindings for Bleak!
import asyncio
from asyncio import AbstractEventLoop

from Foundation import NSDate, NSDefaultRunLoopMode, NSRunLoop
from .CentralManagerDelegate import CentralManagerDelegate

import objc

objc.options.verbose = True

# async def discover(device="hci0", timeout=5.0):
# raise NotImplementedError("CoreBluetooth discover not implemented yet.")
from .PeripheralManagerDelegate import PeripheralManagerDelegate


class Application:
    """
    This is a temporary application class responsible for running the NSRunLoop
    so that events within CoreBluetooth are appropriately handled
    """

    ns_run_loop_done = False
    ns_run_loop_interval = 0.001

    def __init__(self, client: bool = True, loop: AbstractEventLoop = None):
        self.main_loop = asyncio.get_event_loop() if loop is None else loop
        self.main_loop.create_task(self._handle_nsrunloop())
        self.main_loop.create_task(self._is_delegate_ready())

        self.nsrunloop = NSRunLoop.currentRunLoop()

        # This is needed for our Server
        self.central_manager_delegate = CentralManagerDelegate.alloc().init() \
            if client else None
        self.peripheral_manager_delegate = PeripheralManagerDelegate.alloc()\
            .init() if not client else None

    def __del__(self):
        self.ns_run_loop_done = True

    async def _handle_nsrunloop(self):
        while not self.ns_run_loop_done:
            time_interval = NSDate.alloc().initWithTimeIntervalSinceNow_(
                self.ns_run_loop_interval
            )
            self.nsrunloop.runMode_beforeDate_(NSDefaultRunLoopMode, time_interval)
            await asyncio.sleep(0)

    # Develop will have these lines follow their changes
    # async def _central_manager_delegate_ready(self):
    # await self.central_manager_delegate.is_ready()
      
    async def _is_delegate_ready(self):
        if self.central_manager_delegate is not None:
            await self.central_manager_delegate.is_ready()
        else:
            await self.peripheral_manager_delegate.is_ready()


# Server doesn't use this any more, follow client development changes
# Restructure this later: Global isn't the prettiest way of doing this...
global CBAPP
CBAPP = Application()
