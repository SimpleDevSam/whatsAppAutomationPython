import asyncio
from http.client import HTTPException
import json
from typing import Annotated, Dict
from fastapi.params import Depends
from app.application.requests.difiRequest import DifyRequest
from app.application.requests.evolutionRequest import EvolutionApiImageRequest, EvolutionApiTextRequest, Options
from app.application.utils.stringUtils import splitTextForWhatsApp
from app.core.clients.difyClient import DifyClient
from app.core.dependencies.dependencies import getDifyClient
from app.database.redis import push_buffer, fetch_buffer, clear_buffer
from sqlalchemy import select
from app.application.requests.webHookRequest import WebhookData
from app.application.responses.difyResponse import DifyResponse, generateMockDifyResponse
from app.database.connection import async_session
from app.database.models import Company, Images, User
import httpx



class MessageHandler:

    def __init__(self, difyClient: Annotated[DifyClient, Depends(DifyClient)]):
        self.difyClient = difyClient

    async def handleMessage (self, webHookData: WebhookData):
        print(f"Handling message from: {webHookData.data.key.remoteJid}")

        if webHookData.event != "messages.upsert":
            print("Is not messages upserd event")
            raise HTTPException(status_code=400, detail="Unsupported event type")
        
        if (webHookData.data.pushName != "paloma gusmão"):
            print("Is not paloma gusmão")
            raise HTTPException(status_code=400, detail="Unsupported user")
        
        company = await self.getCompanyByWhatsappNumber(webHookData.sender)
        
        if not company:
            print(f"Company not found for whatsapp number: {webHookData.sender}")
            raise HTTPException(status_code=404, detail="Company not found")
        
        
        if  (webHookData.data.key.fromMe == True):
            print("Is from me")
            await self.updateUserBotStatusByCompanyIdAndPhoneNumber(company.id, 0, webHookData.data.key.remoteJid)
            return {"status": "success", "message": "Message from me, no actions taken and status updated to 0"}
        
        user = await self.getUserByUserNumberAndCompanyId(company.id, webHookData.data.key.remoteJid)

        if not user:
            user = await self.createUser(company.id, webHookData.data.key.remoteJid, webHookData.data.pushName)
            print (f"User created for whatsapp number: {webHookData.data.key.remoteJid}")
        
        if user.isBotActive == 0:
            print(f"Bot is not active for user: {user.name}")
            return {"status": "success", "message": "Bot is not active, no actions taken"}
        
        await push_buffer(webHookData.instance + webHookData.data.key.remoteJid, webHookData.data.message.conversation)

        print(f"Message pushed to buffer for user: {user.name} and instance: {webHookData.instance}")

        # await asyncio.sleep(10)

        buffer = await fetch_buffer(webHookData.instance + webHookData.data.key.remoteJid)

        if not buffer:
            print(f"No messages in buffer for user: {user.name} and instance: {webHookData.instance}")
            return {"status": "success", "message": "No messages in buffer, no actions taken"}
        
        if buffer[len(buffer)-1] != webHookData.data.message.conversation:
            print(f"Last message in buffer is not the same as the received message for user: {user.name} and instance: {webHookData.instance}")
            return {"status": "success", "message": "Last message in buffer is not the same as the received message, no actions taken"}
        
        await clear_buffer(webHookData.instance + webHookData.data.key.remoteJid)

        groupedMessages = "\n".join(buffer)

        difyRequest = DifyRequest(
            inputs={},
            query=groupedMessages,
            conversation_id=user.conversationId,
            user=user.whatsappNumber
            )
        
        difyResponse = await self.difyClient.makePostHttpRequest("s", difyRequest.model_dump_json(exclude_none=True))

        # difyResponse = generateMockDifyResponse()

        difyResponse = self.parseDifyResponse(difyResponse)

        if user.conversationId == "" or user.conversationId is None:
            await self.updateUserConversationId(company.id, difyResponse.conversation_id, user.whatsappNumber)

        messages = splitTextForWhatsApp(difyResponse.answer.message)

        for message in messages:
            evolutionRequest = EvolutionApiTextRequest(
                number=user.whatsappNumber,
                text=message
            )

            evolutionResponse = await self.sendTextRequest("s", evolutionRequest.model_dump_json(exclude_none=True), webHookData.instance)

            if not evolutionResponse:
                print(f"Evolution response is empty for user: {user.name} and instance: {webHookData.instance}")
                continue
            
            print(f"Evolution response: {evolutionResponse}")

            await asyncio.sleep(3)
            
        print(buffer)

        productsToSendImage = [item.strip() for item in difyResponse.answer.interestedProductSendImage.split('|')]

        if not productsToSendImage or len(productsToSendImage) == 0:
            return {"status": "success", "message": "No image to send products found"}
        
        for imageName in productsToSendImage:
            image = (await self.getImageByCompanyIdAndImageName(company.id, imageName))
            sendImageMessageRequest = EvolutionApiImageRequest(
                options = Options (delay="10000", presence="composing"),
                number=user.whatsappNumber,
                mediatype="image",
                fileName=image.name,
                caption=image.name,
                media=image.imageUrl
            )

            await self.sendImageRequest("sendImage", sendImageMessageRequest.model_dump_json(exclude_none=True), webHookData.instance)

    
    def parseDifyResponse(self, raw_response: dict) -> DifyResponse:
        if isinstance(raw_response.get('answer'), str):
            try:
                raw_response['answer'] = json.loads(raw_response['answer'])
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in answer: {str(e)}")
        
        return DifyResponse(**raw_response)

    async def getCompanyByWhatsappNumber(self, whatsappNumber: str) -> Company:
        async with async_session() as session:
            stmt = select(Company).where(Company.whatsappNumber == whatsappNumber)
            result = await session.execute(stmt)
            return result.scalars().first()
            
    async def getUserByUserNumberAndCompanyId(self, companyId: int, userNumber:str) -> Company:
        async with async_session() as session:
            stmt = select(User).where(User.whatsappNumber == userNumber and User.company_id == companyId)
            result = await session.execute(stmt)
            return result.scalars().first()
        
    async def getImageByCompanyIdAndImageName(self, companyId: int, imageName:str) -> Images:
        async with async_session() as session:
            stmt = select(Images).where(Images.company_id == companyId).where(Images.name == imageName)
            result = await session.execute(stmt)
            return result.scalars().first()
    
    async def updateUserConversationId(self, companyId: int, conversationId: str, userNumber: str) -> None:
        async with async_session() as session:
            stmt = select(User).where(User.whatsappNumber == userNumber and User.company_id == companyId)
            result = await session.execute(stmt)
            user = result.scalars().first()
            user.conversationId = conversationId
            await session.commit()
            return

    async def createUser(self, companyId: int, userNumber:str, userName:str) -> Company:
        user = User(
            name=userName,
            whatsappNumber=userNumber,
            company_id=companyId
        )
        async with async_session() as session:
            async with session.begin():
                session.add(user)
                await session.commit()
        return user

    async def updateUserBotStatusByCompanyIdAndPhoneNumber(self, companyId: int, status:int, userNumber: str) -> None:
        async with async_session() as session:
            stmt = select(User).where(User.whatsappNumber == userNumber and User.company_id == companyId)
            result = await session.execute(stmt)
            user = result.scalars().first()
            user.isBotActive = status
            await session.commit()
            return
    
    async def make_http_request(self, url: str, data: json) -> Dict[str, any]:
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

    async def sendTextRequest(self, url: str, data: json, instance:str) -> Dict[str, any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"http://localhost:8080/message/sendText/{instance}",
                    data=data, 
                    timeout=30.0,
                    headers=
                    { 
                        "Content-Type": "application/json",
                        "apikey": "automationLife"
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"HTTP request failed: {str(e)}")
                raise

    async def sendImageRequest(self, url: str, data: json, instance:str) -> Dict[str, any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"http://localhost:8080/message/sendMedia/{instance}",
                    data=data, 
                    timeout=30.0,
                    headers=
                    { 
                        "Content-Type": "application/json",
                        "apikey": "automationLife"
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"HTTP request failed: {str(e)}")
                raise






