from pymodbus.client import AsyncModbusTcpClient

from pstg.app.read_signal_config import get_signals_config
from pstg.domain.signal_spec import SignalSpec
from tests.helpers.modbus_test_server import ModbusTestServer


class SignalsModbusTestServer(ModbusTestServer):
    def __init__(self, host: str = "127.0.0.1", device_id: int = 1) -> None:
        super().__init__(host=host, device_id=device_id)
        self.signals_config = get_signals_config()
        self._signals_by_name = {
            signal.signal_name: signal
            for signal in self.signals_config.signals_map
        }

    def set_signal_values(self, values: dict[str, float]) -> None:
        for signal_name, value in values.items():
            self._set_signal_value(signal_name, value)

    def _set_signal_value(self, signal_name: str, value: float) -> None:
        signal = self._signals_by_name[signal_name]
        registers = self._encode_signal_value(signal, value)
        register_writer = (
            self.set_holding_registers
            if signal.fc == 3
            else self.set_input_registers
        )
        register_writer(signal.addr, registers)

    @staticmethod
    def _encode_signal_value(signal: SignalSpec, value: float) -> list[int]:
        if signal.dtype != "f32":
            raise ValueError(f"Unsupported signal dtype: {signal.dtype}")

        return AsyncModbusTcpClient.convert_to_registers(
            value,
            AsyncModbusTcpClient.DATATYPE.FLOAT32,
            word_order=signal.word_order.lower(),
        )
