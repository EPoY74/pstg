import asyncio
import logging

from drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from drivers.read_fc03_holding_register import read_fc03_holding_register
from drivers.read_fc04_input_regoster import read_fc04_input_register


async def poll_device() -> None:
    polled_device = 


async def main() -> None:
    while True:
        await poll_device()


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
