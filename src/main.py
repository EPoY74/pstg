import asyncio
import logging

from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.pdu import ModbusPDU

logger = logging.getLogger(__name__)


async def main() -> None:
    input_regs: ModbusPDU | None = None
    holding_regs: ModbusPDU | None = None

    logger.info("Open Connection")
    pstg_client = AsyncModbusTcpClient(host="10.0.6.10", port=506)

    try:
        is_ok: bool = await pstg_client.connect()
    except Exception as err:
        logger.error("Failed to connect to Modbus server (%s)", err)
        raise ConnectionError("Failed to connect to Modbus server") from err
    if not is_ok or not pstg_client.connected:
        logger.error("Client is not connected")
        raise ConnectionError("Client is not connected")
    logger.info("Connection is opened!")

    try:
        logger.info("Reading input registers (FC04)")
        input_regs = await pstg_client.read_input_registers(
            0, count=1, device_id=1
        )
        logger.info("Registers (FC04) have been read!")
        if (input_regs) and input_regs.isError():
            err_msg = "Received exception from device!"
            logger.error(err_msg)
            pstg_client.close()
            raise RuntimeError(err_msg)
    except ModbusException as err:
        logger.error("Received ModbusException(%s) from library", err)
        pstg_client.close()

    try:
        logger.info("Reading holding registers (FC03)")
        holding_regs = await pstg_client.read_holding_registers(
            0, count=1, device_id=1
        )
        logger.info("Registers (FC03) have been read!")
        if (holding_regs) and holding_regs.isError():
            err_msg = "Received exception from device!"
            logger.error(err_msg)
            pstg_client.close()
            raise RuntimeError(err_msg)
    except ModbusException as err:
        logger.error("Received ModbusException(%s) from library", err)
        pstg_client.close()
        raise err

    # value_int16 = pstg_client.convert_from_registers(
    #     holding_regs.registers, data_type=pstg_client.DATATYPE.UINT16
    # )

    if holding_regs and (not holding_regs.isError()):
        value_int16_holding = holding_regs.registers[0]
        bits_hold = f"{value_int16_holding:016b}"
        logger.info(
            "Got holding registers (FC03) int16: %s (%s)",
            value_int16_holding,
            bits_hold,
        )

    if input_regs and (not input_regs.isError()):
        value_int16_input = input_regs.registers[0]
        bits_inp = f"{value_int16_input:016b}"
        logger.info(
            "Got input registers (FC04) int16: %s (%s)",
            value_int16_input,
            bits_inp,
        )

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
