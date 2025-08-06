from fastapi import FastAPI
from app.application.handleMessage import MessageHandler
from app.core.clients.difyClient import DifyClient
from app.database.init_db import lifespan_wrapper
from app.presentation.controller import MessageHandlerController

app = FastAPI(lifespan=lifespan_wrapper)
messageHandler = MessageHandler(DifyClient())
app.include_router(MessageHandlerController(messageHandler).router)