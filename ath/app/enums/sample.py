from enum import Enum


class Status(str, Enum):
    UPLOADING = "uploading"
    PARSING = "parsing"
    PROCESSING = "processing"
    RENDERING = "rendering"
    DONE = "done"
    FAILED = "failed"
