# presentation/controllers/webhook_controller.py
from typing_extensions import Annotated
from fastapi import APIRouter, HTTPException, Request, Depends
from app.application.requests.webHookRequest import WebhookData
from app.application.handleMessage import MessageHandler

class MessageHandlerController:
    def __init__(self, handler: Annotated[MessageHandler, Depends(MessageHandler)]):
        self.router = APIRouter()
        self.handler= handler
        self.router.add_api_route("/", self.home, methods=["GET"])
        self.router.add_api_route("/webhook", self.handle_webhook, methods=["POST"])

    async def home(self):
        return {"message": "Webhook Service Running"}

    async def handle_webhook(self, request: Request):
        print("Receiving webhook request")
        try:
            raw_data = await request.json()
            try:
                webhook_data = WebhookData(**raw_data)
            except Exception as e:
                raise HTTPException(status_code=422, detail=str(e))
            
            return await self.handler.handleMessage(webhook_data)

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")