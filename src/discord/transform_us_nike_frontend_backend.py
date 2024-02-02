from typing import Any
import math
from dateutil.parser import parse as parse_datetime_string # type: ignore

from .types import DiscordMessage

from src.constants import ChannelId, SizeInfo, InfoSource
from src.tables import PrimaryMarketInformationTable, PrimaryMarketInformationTableInfoSource


def str_to_datetime(x: str) -> int:
    return int(parse_datetime_string(x).timestamp())


def extract_retail_price(msg: str) -> float:
    """
    Extracts the retail price from the given message.
    """
    try:
        return float(msg.split("USD")[0])
    except ValueError:
        return math.nan


def extract_discounted_price(msg: str) -> float:
    """
    Extracts the discounted price from the given message.
    """
    try:
        return float(msg.split("(")[-1].split("USD")[0])
    except ValueError:
        return math.nan


def parse_sizes(size_info: str) -> list[dict[str, Any]]:
    """
    Parse the size information and return a list of dictionaries containing size and stock.
    """
    result = []
    i = 0
    curr_size = ""
    curr_stock = ""
    bracket_count = 0
    while i < len(size_info):
        if size_info[i] == "[":
            i += 1
            bracket_count += 1
            if bracket_count == 1:
                # parse size
                while size_info[i].isdigit():
                    curr_size += size_info[i]
                    i += 1
            else:
                # parse stock
                while size_info[i] != "]":
                    curr_stock += size_info[i]
                    i += 1
        if size_info[i] == ")":
            # end of a size info
            # link is add to cart, not needed
            try:
                result.append({
                    "size": float(curr_size),
                    "stock": curr_stock,
                })
            except ValueError:
                pass
            curr_size = ""
            curr_stock = ""
            bracket_count = 0
        i += 1
    return result


def extract_retail_link(msg):
    link = ""
    i = 0
    while i < len(msg):
        if msg[i] == "(":
            # parse size
            i += 1
            while msg[i] != ")":
                link += msg[i]
                i += 1
            if "nike.com" in link:
                return link
        i += 1
    return ""


def parse_platform_links(links):
    i = 0
    site_name = ""
    stock_x_link = None
    goat_link = None
    while i < len(links):
        if links[i] == "[":
            i += 1
            curr_site_name = ""
            while links[i] != "]":
                curr_site_name += links[i]
                i += 1
            site_name = curr_site_name
        elif links[i] == "(":
            i += 1
            curr_link = ""
            while links[i] != ")":
                curr_link += links[i]
                i += 1
            if site_name == "StockX":
                stock_x_link = curr_link
            elif site_name == "GOAT":
                goat_link = curr_link
        i += 1
    return {'stockXLink': stock_x_link, 'goatLink': goat_link}


def parse_fields(fields: dict) -> dict:
    field_values = {}
    for field in fields:
        field_name = field['name'].lower()
        field_value = field['value']
        if field_name == "sku":
            field_values["sku"] = field_value
        elif field_name == "status":
            field_values["active"] = 'active' in field_value.lower()
        elif field_name == "size [stock]":
            field_values["availableSizes"] = parse_sizes(field_value)
        elif field_name == "discount / promo / cod":
            discounted_price = extract_discounted_price(field_value)
            if not math.isnan(discounted_price):
                field_values["discountedPrice"] = discounted_price
        elif field_name == "channel":
            link = extract_retail_link(field_value)
            field_values["atcLink"] = link
            field_values["retailLink"] = link
        elif field_name == "useful links":
            platform_links = parse_platform_links(field_value)
            field_values["stockXLink"] = platform_links['stockXLink']
            field_values["goatLink"] = platform_links['goatLink']
    return field_values


def transform_us_nike_frontend_backend(db, json) -> DiscordMessage:
    id = json['id']
    datetime = str_to_datetime(json['timestamp'])
    embed = json['embeds'][0]
    title = embed['title']
    live = "live" in embed['description'].lower()
    retail_price = extract_retail_price(embed['description'])
    image_url = embed['thumbnail']['url']
    fields = embed['fields']
    field_values = parse_fields(fields)

    available_sizes: dict[str, SizeInfo] = {}
    for size_and_stock in field_values.get("availableSizes", []):
        size = size_and_stock['size']
        stock = size_and_stock['stock']
        available_sizes[str(size)] = {
            "atc_link": str(field_values.get("atcLink", "")),
            "stock": "N/A" if stock == "" else stock
        }

    info = PrimaryMarketInformationTable(
        db,
        id,
        title,
        str(field_values.get("sku", "")),
        field_values.get("discountedPrice", retail_price),
        available_sizes,
        image_url,
        str(field_values.get("retailLink", "")),
        datetime,
        PrimaryMarketInformationTableInfoSource(InfoSource.DISCORD, ChannelId.US_NIKE_FRONTEND_BACKEND),
        str(field_values.get("stockXLink", "")),
        str(field_values.get("goatLink", "")),
    )

    return {
        "info": info,
        "isValid": live and field_values.get("active", False)
    }
