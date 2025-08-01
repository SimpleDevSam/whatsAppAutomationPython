from typing import Any, Dict, Optional
from pydantic import BaseModel

class MessageKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str

class MessageContextInfo(BaseModel):
    deviceListMetadata: Optional[Dict[str, Any]] = None
    deviceListMetadataVersion: Optional[int] = None
    messageSecret: Optional[str] = None

class MessageContent(BaseModel):
    conversation: Optional[str] = None
    messageContextInfo: Optional[MessageContextInfo] = None

class MessageKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str

class MessageData(BaseModel):
    key: MessageKey
    pushName: str
    message: MessageContent
    messageType: str
    messageTimestamp: int
    owner: str
    source: str

class WebhookData(BaseModel):
    event: str
    instance: str
    data: MessageData
    destination: str
    date_time: str
    sender: str
    server_url: str
    apikey: str

