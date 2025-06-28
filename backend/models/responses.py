from pydantic import BaseModel

class UploadResponse(BaseModel):
    message: str
    session_id: str
    samples: int

