from pydantic import BaseModel


class UploadResponse(BaseModel):
    object_key: str
    upload_url: str

class DownloadResponse(BaseModel):
    download_url: str

