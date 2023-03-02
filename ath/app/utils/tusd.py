from app.core.config import Settings, get_settings

settings: Settings = get_settings()


def tusd_upload_url() -> str:
    url: str = (
        f"http://"
        f"{settings.TUSD_HOST}:"
        f"{settings.TUSD_PORT}"
        f"{settings.TUSD_ENDPOINT}"
    )
    return url
