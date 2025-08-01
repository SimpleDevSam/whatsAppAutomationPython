import json
import random
import uuid
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone

class AnswerContent(BaseModel):
    sendCatalog: Optional[bool] = False
    sendValueTable: Optional[bool] = False
    productValueTable: Optional[str] = None
    interestedProductSendImage: Optional[str] = None
    message: str

class UsageMetrics(BaseModel):
    prompt_tokens: int
    prompt_unit_price: str
    prompt_price_unit: str
    prompt_price: str
    completion_tokens: int
    completion_unit_price: str
    completion_price_unit: str
    completion_price: str
    total_tokens: int
    total_price: str
    currency: str
    latency: float

class Metadata(BaseModel):
    annotation_reply: Optional[Any] = None
    retriever_resources: List[Any] = []
    usage: UsageMetrics

class DifyResponse(BaseModel):
    event: str
    task_id: str
    id: str
    message_id: str
    conversation_id: str
    mode: str
    answer: Union[str, AnswerContent]
    metadata: Metadata
    created_at: datetime

    @property
    def parsed_answer(self) -> AnswerContent:
        try:
            return AnswerContent(**json.loads(self.answer))
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse answer: {str(e)}")


def generateMockDifyResponse() -> Dict[str, Any]:
    """Generates a mock response that exactly matches the real API format"""
    
    # Generate random IDs and consistent values
    task_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    # Create the exact answer JSON string structure
    answer_json = """{
  "sendCatalog": false,
  "sendValueTable": false,
  "productValueTable": "",
  "interestedProductSendImage": "",
  "message": "Desculpe, não entendi sua mensagem. Como posso te ajudar hoje? 💚"
}"""
    
    # Generate realistic usage metrics (exactly matching API format)
    prompt_tokens = random.randint(1500, 2000)
    completion_tokens = random.randint(50, 100)
    
    return {
        "event": "message",
        "task_id": task_id,
        "id": message_id,
        "message_id": message_id,
        "conversation_id": conversation_id,
        "mode": "advanced-chat",
        "answer": answer_json,  # Exact string format with newlines and spaces
        "metadata": {
            "annotation_reply": None,
            "retriever_resources": [],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "prompt_unit_price": "0.0005",
                "prompt_price_unit": "0.001",
                "prompt_price": f"{prompt_tokens * 0.0005:.7f}",
                "completion_tokens": completion_tokens,
                "completion_unit_price": "0.0015",
                "completion_price_unit": "0.001",
                "completion_price": f"{completion_tokens * 0.0015:.7f}",
                "total_tokens": prompt_tokens + completion_tokens,
                "total_price": f"{(prompt_tokens * 0.0005) + (completion_tokens * 0.0015):.7f}",
                "currency": "USD",
                "latency": round(random.uniform(0.8, 1.5), 6)
            }
        },
        "created_at": int(datetime.now(timezone.utc).timestamp())
    }
