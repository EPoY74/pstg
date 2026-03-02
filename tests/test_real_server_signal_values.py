import asyncio

import pytest

from pstg.app.read_signal_config import get_signals_config
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.simulator.signals_server import (
    DEFAULT_SIGNAL_VALUES,
    build_signals_server_config,
)
from pstg.simulator.server import DevModbusServer
from tests.helpers.signals_modbus_test_server import SignalsModbusTestServer


def test_signal_server_serves_expected_signal_values() -> None:
    async def scenario() -> None:
        expected_values = {
            "PT1": 1.5,
            "PT2": 2.5,
            "PT3": 3.5,
            "FlowPerHour": 120.25,
            "FlowAmount": 456.75,
        }
        signals_config = get_signals_config()

        server = SignalsModbusTestServer()
        server.set_signal_values(expected_values)
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(server.host, server.port)
            response = await client.read_holding_registers(
                address=signals_config.offset,
                count=signals_config.read_count,
                device_id=server.device_id,
            )

            assert response.isError() is False
            for signal in signals_config.signals_map:
                start = signal.addr - signals_config.offset
                actual_value = client.convert_from_registers(
                    response.registers[start : start + 2],
                    client.DATATYPE.FLOAT32,
                    word_order=signal.word_order.lower(),
                )
                assert actual_value == pytest.approx(
                    expected_values[signal.signal_name]
                )
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())


def test_runtime_signal_server_serves_expected_signal_values() -> None:
    async def scenario() -> None:
        signals_config = get_signals_config()
        config = build_signals_server_config(port=1506)
        server = DevModbusServer(config)
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(config.host, config.port)
            response = await client.read_holding_registers(
                address=signals_config.offset,
                count=signals_config.read_count,
                device_id=config.device_id,
            )

            assert response.isError() is False
            for signal in signals_config.signals_map:
                start = signal.addr - signals_config.offset
                actual_value = client.convert_from_registers(
                    response.registers[start : start + 2],
                    client.DATATYPE.FLOAT32,
                    word_order=signal.word_order.lower(),
                )
                assert actual_value == pytest.approx(
                    DEFAULT_SIGNAL_VALUES[signal.signal_name]
                )
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())
