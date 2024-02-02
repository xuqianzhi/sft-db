from typing import Any

from google.cloud import firestore  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter  # type: ignore

from src.constants import SizeInfo, InfoSource, ChannelId


class PrimaryMarketInformationTableInfoSource:
    base_source: InfoSource
    detailed_source: str

    def __init__(self, base_source: InfoSource, discord_channel_id: ChannelId | None=None) -> None:
        self.base_source = base_source

        match base_source:
            case InfoSource.DISCORD:
                assert discord_channel_id
                self.detailed_source = f"{InfoSource.DISCORD}-{discord_channel_id}"
            case default:
                self.detailed_source = ""

    def get_detailed_source(self) -> str:
        return self.detailed_source


class PrimaryMarketInformationTable:
    db: firestore.Client
    doc_ref: firestore.DocumentReference
    id: str
    title: str
    sku: str
    retail_price: float
    available_sizes: dict[str, SizeInfo]
    image_url: str
    retail_link: str
    datetime: int
    source: PrimaryMarketInformationTableInfoSource
    stockx_link: str | None
    goat_link: str | None

    def __init__(
        self,
        db: firestore.Client,
        id: str,
        title: str,
        sku: str,
        retail_price: float,
        available_sizes: dict[str, SizeInfo],
        image_url: str,
        retail_link: str,
        datetime: int,
        source: PrimaryMarketInformationTableInfoSource,
        stockx_link: str | None,
        goat_link: str | None,
    ):
        self.id = id
        self.title = title
        self.sku = sku
        self.retail_price = retail_price
        self.available_sizes = available_sizes
        self.image_url = image_url
        self.retail_link = retail_link
        self.stockx_link = stockx_link
        self.goat_link = goat_link
        self.datetime = datetime
        self.source = source

        self.db = db
        self.doc_ref = db.collection("PrimaryMarketInfo").document(id)

    def __repr__(self) -> str:
        return str(self.get_document())

    def __str__(self) -> str:
        return str(self.get_document())

    def get_document(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "sku": self.sku,
            "retailPrice": self.retail_price,
            "availableSizes": self.available_sizes,
            "imageUrl": self.image_url,
            "stockXLink": self.stockx_link,
            "goatLink": self.goat_link,
            "datetime": self.datetime,
            "source": self.source.get_detailed_source(),
        }

    def write_document(self):
        document = self.get_document()
        self.doc_ref.set(document)

    @staticmethod
    def get_collection_name():
        return "PrimaryMarketInfo"

    @staticmethod
    def get_most_recent_doc(db: firestore.Client, source: PrimaryMarketInformationTableInfoSource | None = None) -> dict | None:
        ref = db.collection("PrimaryMarketInfo")

        query = ref.where(
            filter=(FieldFilter("source", "==", source.get_detailed_source()))) if source else ref
        query = (query
                 .order_by("datetime", direction=firestore.Query.DESCENDING)
                 .limit(1))
        results = query.get()
        return list(results)[0].to_dict() if results else None
