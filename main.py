from fastapi import FastAPI
from database.init_db import lifespan_wrapper
from presentation.controller import router

app = FastAPI(lifespan=lifespan_wrapper)

app.include_router(router)


