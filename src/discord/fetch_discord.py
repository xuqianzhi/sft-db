import os
import requests

from typing import Any

from dotenv import load_dotenv
from dateutil.parser import parse as parse_datetime_string

from .transform_us_nike_frontend_backend import transform_us_nike_frontend_backend

from src.constants import ChannelId
from src.tables import PrimaryMarketInformationTable

load_dotenv()
DISCORD_AUTH = os.getenv("DISCORD_AUTH")


def fetch_discord_msgs(db: Any, channel_id: ChannelId) -> list[PrimaryMarketInformationTable]:
    headers = {"authorization": str(DISCORD_AUTH)}
    response = requests.get(
        f"https://discord.com/api/v8/channels/{channel_id}/messages", headers=headers)
    if not response.ok:
        raise Exception(
            f"Failed to fetch from discord; status code: {response.status_code}")
    json_res = response.json()

    match channel_id:
        case ChannelId.US_NIKE_FRONTEND_BACKEND:
            sorted_res = sorted(json_res, key=lambda x: parse_datetime_string(x['timestamp']).timestamp(), reverse=True)
            decoded_res = [transform_us_nike_frontend_backend(db, x) for x in sorted_res]
            filtered_res = filter(lambda x: x["isValid"], decoded_res)
            return [x["info"] for x in filtered_res]
        case default:
            return []

    


