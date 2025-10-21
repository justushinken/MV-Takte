#!/usr/bin/env python3
import asyncio
import logging
from pymodbus.datastore import (ModbusDeviceContext, ModbusSequentialDataBlock, ModbusServerContext)
import modbus.server_async as server_async  # type: ignore[import-not-found]

_logger = logging.getLogger(__name__)

def update_values(context, value):
    """Update values in server.
    """
    func_code = 3
    device_id = 0x00
    address = 0x00

    # values needs to be a list of int or bool in modbus
    value_you_want_to_set = value  # <------- hier letzlich den Wert setzen @Sebastian
    values = [value_you_want_to_set]

    # sets the values in the datastore - at address 0x00 / meaning first word in the block
    # before blocks from address hex 0x00/ dec 0 to hex 0x09/ dec 9 (10 values) were initialized
    context[device_id].setValues(func_code, address, values)

    # for debugging fetches the values from the datastore - just to check if it was set
    #check = context[device_id].getValues(func_code, address, count=5)

    txt = f"updating_task: values: {values!s} at address {address!s}"
    print(txt)
    _logger.debug(txt)

def setup_server(cmdline=None):
    """Run server setup."""
    # The datastores only respond to the addresses that are initialized
    # If you initialize a DataBlock to addresses of 0x00 to 0xFF, a request to
    # 0x100 will respond with an invalid address exception.
    # This is because many devices exhibit this kind of behavior (but not all)

    # Continuing, use a sequential block without gaps.
    datablock = ModbusSequentialDataBlock(0x00, [0] * 10)  # Initialize 10 blocks with 0 - to see if it is working
    device_context = ModbusDeviceContext(di=datablock, co=datablock, hr=datablock, ir=datablock)
    context = ModbusServerContext(devices=device_context, single=True)
    return server_async.setup_server(
        description="Run asynchronous server.", context=context, cmdline=cmdline
    )

if __name__ == "__main__":
    # default port in pymodbus is 5020 - normal modbus port is 502
    run_args = setup_server(cmdline=None)
    asyncio.run(server_async.run_async_server(run_args), debug=True)