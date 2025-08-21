from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from .db import create_db_and_tables, get_session
from .models import Account
from .routers import accounts, roommates, splits, transactions
from .services.services import compute_balance


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"]
)


app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(roommates.router)
app.include_router(splits.router)


@app.get("/account-balances", response_model=dict[int, Decimal])
def get_account_balances(*, session: Session = Depends(get_session)):
    balances = {}
    for account in session.query(Account).all():
        balances[account.id] = compute_balance(session, account)
    return balances
