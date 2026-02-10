import asyncio
import logging

from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.logging import Log
from pymodbus.pdu import ModbusPDU

logger = logging.getLogger(__name__)


async def main() -> None:
    input_regs: ModbusPDU | None = None
    holding_regs: ModbusPDU | None = None
    pstg_client = AsyncModbusTcpClient(host="10.0.6.10", port=506)
    logger.info("Open Connection")
    try:
        is_ok: bool = await pstg_client.connect()
    except Exception as err:
        logger.error("Failed to connect to Modbus server (%s)", err)
        raise ConnectionError("Failed to connect to Modbus server") from err
    if not is_ok or not pstg_client.connected:
        logger.error("Client is not connected")
        raise ConnectionError("Client is not connected")
    # assert pstg_client.connected, (
    #     "Connection is not connected!"
    # )  # из-за асинхронности может обманывать
    logger.info("Connection is opened!")
    try:
        logger.info("Reading input registers (FC04)")
        input_regs = await pstg_client.read_input_registers(
            0, count=2, device_id=1
        )
        logger.info("Registers (FC04) have been read!")
    except ModbusException as err:
        logger.error("Received ModbusException(%s) from library", err)
        if (input_regs) and (input_regs.isError()):
            logger.error("Received exception from device (%s)", err)
            pstg_client.close()
            raise err

    try:
        logger.info("Reading holding registers (FC03)")
        holding_regs = await pstg_client.read_holding_registers(
            0, count=2, device_id=1
        )
        logger.info("Registers (FC03) have been read!")
    except ModbusException as err:
        logger.error("Received ModbusException(%s) from library", err)
        if (holding_regs) and (holding_regs.isError()):
            logger.error("Received exception from device (%s)", err)
        pstg_client.close()
        raise err
    value_int16 = pstg_client.convert_from_registers(
        holding_regs.registers, data_type=pstg_client.DATATYPE.UINT16
    )
    logger.info("Got int16: %s", value_int16)
    logger.info("Close connection")
    pstg_client.close()


if __name__ == "__main__":
    # ✅ Настройка логов только при запуске как скрипт
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Start Pump Station Telemetry Gateway")
    asyncio.run(main(), debug=True)
    logger.info("Stop Pump Station Telemetry Gateway")
