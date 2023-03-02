from enum import Enum


class HookName(str, Enum):
    PRE_CREATE = "pre-create"
    POST_FINISH = "post-finish"
