from collections.abc import Awaitable, Callable

from pymodbus.pdu import ModbusPDU

Reader = Callable[..., Awaitable[ModbusPDU | None]]
