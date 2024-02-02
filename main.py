import firebase_admin
from firebase_admin import firestore, credentials

from src.discord import (
    fetch_discord_msgs,
)
from src.tables import (
    PrimaryMarketInformationTable,
    PrimaryMarketInformationTableInfoSource
)
from src.constants import (
    ChannelId,
    InfoSource,
)


cred = credentials.Certificate(
    "sft-python-firebase-adminsdk-z1ywq-cd38aef86e.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()


infos: list[PrimaryMarketInformationTable] = fetch_discord_msgs(
    db, ChannelId.US_NIKE_FRONTEND_BACKEND)
latest_msg = PrimaryMarketInformationTable.get_most_recent_doc(
    db, source=PrimaryMarketInformationTableInfoSource(
        InfoSource.DISCORD,
        ChannelId.US_NIKE_FRONTEND_BACKEND
    ))
if latest_msg:
    latest_info, latest_datetime = latest_msg['sku'], latest_msg['datetime']
else:
    latest_datetime = 0

write_count = 0
for info in infos:
    if info.datetime > latest_datetime:
        info.write_document()
        write_count += 1
print(f"list count: {len(infos)}; write count: {write_count}")
