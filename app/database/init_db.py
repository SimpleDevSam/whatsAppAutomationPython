import asyncio
from fastapi import FastAPI
from app.database.connection import engine
from contextlib import asynccontextmanager
from app.database.models import Base

async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan_wrapper(app:FastAPI):
    await create_database()
    yield