from fastapi import FastAPI
from app.database.init_db import lifespan_wrapper
from app.presentation.controller import router

app = FastAPI(lifespan=lifespan_wrapper)

app.include_router(router)


