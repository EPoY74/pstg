#  Проверяет fallback FC04 -> FC03, когда FC04 вернул DEVICE error.
import asyncio

from pstg.app import collector
from pstg.domain.connection_state import ConnectionState
from pstg.domain.error_info import ErrorInfo
from pstg.domain.kind_state import KindState
from pstg.domain.raw_block_result import RawBlockResult
from pstg.domain.registers_modbus_device_settings import (
    RegistersModbusDeviceSettings,
)


def test_poll_device_uses_fc03_after_fc04_device_error(monkeypatch) -> None:
    call_order: list[int] = []

    async def fake_read_block(reader, fc, device, settings):
        call_order.append(fc)

        if fc == 4:
            return (
                RawBlockResult(
                    fc=4,
                    ok=False,
                    current_error_info=ErrorInfo(
                        message="fc04 device error",
                        kind=KindState.DEVICE,
                        exception_code=2,
                    ),
                ),
                True,
            )

        return (
            RawBlockResult(
                fc=3,
                ok=True,
                registers=[1, 2, 3],
            ),
            True,
        )

    monkeypatch.setattr(collector, "read_block", fake_read_block)

    result = asyncio.run(
        collector.poll_device(
            device_being_polled=object(),
            device_poll_settings=RegistersModbusDeviceSettings(
                device_id=1,
                offset=0,
                read_count=3,
            ),
        )
    )

    assert call_order == [4, 3]
    assert result.connection_state == ConnectionState.UP
    assert len(result.blocks) == 2
    assert result.blocks[0].fc == 4
    assert result.blocks[1].fc == 3
    assert result.blocks[1].registers == [1, 2, 3]
