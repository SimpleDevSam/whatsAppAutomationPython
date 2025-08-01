from fastapi import APIRouter, HTTPException, Request
from app.application.requests.webHookRequest import WebhookData
from app.application.handleMessage import handleMessage

router = APIRouter()

@router.get("/")

@router.post("/webhook")
async def handle_webhook(request:Request):
    print(f"Receiving webhook request")
    try:
        raw_data = await request.json()
        try:
            webhook_data = WebhookData(**raw_data)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
        
        return await handleMessage(webhook_data)

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")