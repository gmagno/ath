import json
import uuid

from rich import print
from tusclient import client
from tusclient.exceptions import TusCommunicationError

from app.core.config import Settings, get_settings
from app.utils.tusd import tusd_upload_url

settings: Settings = get_settings()


async def upload_aio(csv_file: str) -> None:
    upload_id: str = str(uuid.uuid4())
    url: str = tusd_upload_url()
    tusd_client = client.TusClient(url)
    uploader = tusd_client.async_uploader(
        csv_file,
        chunk_size=settings.TUSD_UPLOAD_CHUNK,
        metadata={"upload_id": upload_id},
    )
    print(f"CSV sample uploaded with upload_id: '{upload_id}'")
    try:
        await uploader.upload()
    except TusCommunicationError as e:
        response = json.loads(e.response_content)
        print(f"Error uploading file [{response=}]")

    print("Successfully uploaded file!")
