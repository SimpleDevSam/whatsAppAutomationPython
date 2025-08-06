import json
from typing import Dict
import httpx


class DifyClient:
    
    async def makePostHttpRequest(self, url: str, data: json) -> Dict[str, any]:
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.dify.ai/v1/chat-messages",
                    data=data, 
                    timeout=30.0,
                    headers=
                    { 
                        "Content-Type": "application/json",
                        "Authorization": "Bearer app-WX39XW7PBrzvvX0NfzlgjLVw"
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"HTTP request failed: {str(e)}")
                raise