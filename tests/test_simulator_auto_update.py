import asyncio

from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register
from pstg.simulator.config import RegisterBlockConfig, SimulatorConfig
from pstg.simulator.server import DevModbusServer


def test_dev_modbus_server_updates_registers_by_timer() -> None:
    async def scenario() -> None:
        config = SimulatorConfig(
            host="127.0.0.1",
            port=1505,
            device_id=1,
            input_registers=[
                RegisterBlockConfig(
                    address=0,
                    values=[10, 20],
                    interval_s=0.1,
                    step=5,
                ),
            ],
            holding_registers=[],
        )
        server = DevModbusServer(config)
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(config.host, config.port)

            first_response = await read_fc04_input_register(
                client,
                offset=0,
                read_count=2,
                plc_id=config.device_id,
            )
            assert first_response is not None
            first_registers = list(first_response.registers)

            await asyncio.sleep(0.25)

            second_response = await read_fc04_input_register(
                client,
                offset=0,
                read_count=2,
                plc_id=config.device_id,
            )
            assert second_response is not None
            assert second_response.registers[0] > first_registers[0]
            assert second_response.registers[1] > first_registers[1]
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())
