from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    EXPORTING = "exporting"
    DONE = "done"
    ERROR = "error"


tasks: dict = {}
