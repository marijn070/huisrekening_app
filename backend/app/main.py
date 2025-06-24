from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import create_db_and_tables
from .routers import accounts, roommates, splits, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(roommates.router)
app.include_router(splits.router)
