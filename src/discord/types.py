from typing import Any, TypedDict
from src.tables import PrimaryMarketInformationTable

class DiscordMessage(TypedDict):
    info: PrimaryMarketInformationTable
    isValid: bool