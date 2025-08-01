from typing import Optional
from pydantic import BaseModel


class FileObject(BaseModel):
    type: str
    transfer_method: str
    url: str

class DifyRequest(BaseModel):
    inputs: object
    query: str
    response_mode: str = "blocking"
    conversation_id: Optional[str] = ""
    user :str
    files: list[FileObject] = []
    class Config:
        json_encoders = {
            # Add custom serializers if needed for any special types
        }
                