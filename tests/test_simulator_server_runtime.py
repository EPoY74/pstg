import asyncio

from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register
from pstg.simulator.config import RegisterBlockConfig, SimulatorConfig
from pstg.simulator.server import DevModbusServer


def test_dev_modbus_server_serves_configured_input_registers() -> None:
    async def scenario() -> None:
        config = SimulatorConfig(
            host="127.0.0.1",
            port=1504,
            device_id=1,
            input_registers=[
                RegisterBlockConfig(address=0, values=[111, 222, 333]),
            ],
            holding_registers=[],
        )
        server = DevModbusServer(config)
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(config.host, config.port)
            response = await read_fc04_input_register(
                client,
                offset=0,
                read_count=3,
                plc_id=config.device_id,
            )
            assert response is not None
            assert response.isError() is False
            assert response.registers == [111, 222, 333]
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())
