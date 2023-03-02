from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class StorageType(str, Enum):
    FILE = "filestore"
    S3 = "s3store"


class FileStorage(BaseModel):
    type: Literal[StorageType.FILE] = Field(alias="Type")
    path: str = Field(alias="Path")


class S3Storage(BaseModel):
    type: Literal[StorageType.S3] = Field(alias="Type")
    bucket: str = Field(alias="Bucket")
    key: str = Field(alias="Key")


class Upload(BaseModel):
    id: str = Field(alias="ID")
    size: int = Field(alias="Size")
    size_is_deferred: bool = Field(alias="SizeIsDeferred")
    offset: int = Field(alias="Offset")
    is_final: bool = Field(alias="IsFinal")
    is_partial: bool = Field(alias="IsPartial")
    partial_uploads: Optional[List[str]] = Field(alias="PartialUploads")
    metadata: Dict = Field(alias="MetaData")
    storage: Optional[Union[FileStorage, S3Storage]] = Field(
        alias="Storage", default=None
    )


class HttpRequest(BaseModel):
    method: str = Field(alias="Method")
    uri: str = Field(alias="URI")
    remote_addr: str = Field(alias="RemoteAddr")
    header: Dict = Field(alias="Header")


class HookBody(BaseModel):
    upload: Upload = Field(alias="Upload")
    http_request: HttpRequest = Field(alias="HTTPRequest")
