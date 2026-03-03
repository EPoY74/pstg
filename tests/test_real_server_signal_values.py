import asyncio

import pytest

from pstg.app.read_signal_config import get_signals_config
from pstg.drivers.open_connection_modbus_tcp import open_connection_modbus_tcp
from pstg.drivers.read_fc04_input_regoster import read_fc04_input_register
from pstg.simulator.signals_server import (
    DEFAULT_HOLDING_REGISTERS,
    DEFAULT_INPUT_REGISTERS,
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
                address=signals_config.start_address_of_block,
                count=signals_config.read_count,
                device_id=server.device_id,
            )

            assert response.isError() is False
            for signal in signals_config.signals_map:
                start = signal.addr - signals_config.start_address_of_block
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
                address=signals_config.start_address_of_block,
                count=signals_config.read_count,
                device_id=config.device_id,
            )

            assert response.isError() is False
            for signal in signals_config.signals_map:
                start = signal.addr - signals_config.start_address_of_block
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


def test_runtime_signal_server_serves_fc_and_updates_values_over_time() -> None:
    async def scenario() -> None:
        signals_config = get_signals_config()
        config = build_signals_server_config(port=1507)
        server = DevModbusServer(config)
        await server.start()

        client = None
        try:
            client = await open_connection_modbus_tcp(config.host, config.port)

            first_fc04 = await read_fc04_input_register(
                client,
                offset=DEFAULT_INPUT_REGISTERS[0].address,
                read_count=len(DEFAULT_INPUT_REGISTERS[0].values),
                plc_id=config.device_id,
            )
            assert first_fc04 is not None

            first_fc03 = await client.read_holding_registers(
                address=DEFAULT_HOLDING_REGISTERS[0].address,
                count=len(DEFAULT_HOLDING_REGISTERS[0].values),
                device_id=config.device_id,
            )
            assert first_fc03.isError() is False

            first_signals = await client.read_holding_registers(
                address=signals_config.start_address_of_block,
                count=signals_config.read_count,
                device_id=config.device_id,
            )
            assert first_signals.isError() is False
            first_pt1 = client.convert_from_registers(
                first_signals.registers[0:2],
                client.DATATYPE.FLOAT32,
                word_order="little",
            )

            await asyncio.sleep(2.2)

            second_fc04 = await read_fc04_input_register(
                client,
                offset=DEFAULT_INPUT_REGISTERS[0].address,
                read_count=len(DEFAULT_INPUT_REGISTERS[0].values),
                plc_id=config.device_id,
            )
            assert second_fc04 is not None
            assert second_fc04.registers[0] > first_fc04.registers[0]

            second_fc03 = await client.read_holding_registers(
                address=DEFAULT_HOLDING_REGISTERS[0].address,
                count=len(DEFAULT_HOLDING_REGISTERS[0].values),
                device_id=config.device_id,
            )
            assert second_fc03.isError() is False
            assert second_fc03.registers[0] > first_fc03.registers[0]

            second_signals = await client.read_holding_registers(
                address=signals_config.start_address_of_block,
                count=signals_config.read_count,
                device_id=config.device_id,
            )
            assert second_signals.isError() is False
            second_pt1 = client.convert_from_registers(
                second_signals.registers[0:2],
                client.DATATYPE.FLOAT32,
                word_order="little",
            )
            assert second_pt1 > first_pt1
        finally:
            if client is not None:
                client.close()
            await server.stop()

    asyncio.run(scenario())
