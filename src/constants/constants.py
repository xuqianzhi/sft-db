from enum import StrEnum
from typing import TypedDict

class StockInfo(StrEnum):
    LOW = 'LOW'
    MED = 'MEDIUM'
    HIGH = 'HIGH'
    NA = 'N/A'


class SizeInfo(TypedDict):
    atc_link: str
    stock: StockInfo


class InfoSource(StrEnum):
    DISCORD = 'Discord'


class ChannelId(StrEnum):
    NIKE_US = "1161659215530688532"
    US_NIKE_FRONTEND_BACKEND = "1068225788530413588"