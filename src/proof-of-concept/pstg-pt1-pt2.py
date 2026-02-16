"""
20260216: Самая первая версия опросчика для датчиков давления PT1 и  PT2. 
Тестовая.
Считывает  через FC04 и FC03 2 word с устройства id = 1 с адресов 56 и 58
IP  адрес и порт - хардкод 
"""

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
        logger.info("Reading PT1 input registers (FC04)")
        input_regs = await pstg_client.read_input_registers(
            56, count=2, device_id=1
        )
        logger.info("PT1 (FC04) have been read!")
        if (input_regs) and input_regs.isError():
            err_msg = "Received exception from device!"
            logger.error(err_msg)
            pstg_client.close()
            raise RuntimeError(err_msg)
    except ModbusException as err:
        logger.error("Received ModbusException(%s) from library", err)
        pstg_client.close()
    if input_regs and (not input_regs.isError()):
        value_int16_input = input_regs.registers[0]
        logger.info(
            "Got PT1 input registers (FC04) float32: %s",
            value_int16_input,
        )
        logger.info(pstg_client.convert_from_registers(
            input_regs.registers[0:2], pstg_client.DATATYPE.FLOAT32, word_order="little"))

    try:
        logger.info("Reading PT2 from holding registers (FC03)")
        holding_regs = await pstg_client.read_holding_registers(
            58, count=2, device_id=1
        )
        logger.info("PT2 (FC03) have been read!")
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
        value_int16_holding = holding_regs.registers
        # bits_hold = f"{value_int16_holding:016b}"
        logger.info(
            "Got holding registers PT2 (FC03) float32: %s ",
            value_int16_holding,
            # bits_hold,
        )
        logger.info(pstg_client.convert_from_registers(
            holding_regs.registers[0:2], pstg_client.DATATYPE.FLOAT32, word_order="little"))

    logger.info("Close connection")
    pstg_client.close()


if __name__ == "__main__":
    # ✅ Настройка логов только при запуске как скрипт
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Start Pump Station Telemetry Gateway")
    asyncio.run(main(), debug=True)
    logger.info("Stop Pump Station Telemetry Gateway")
