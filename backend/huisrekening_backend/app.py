from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from .db import create_db_and_tables, engine
from .models import (
    Account,
    AccountCreate,
    AccountPublic,
    AccountType,
    AccountUpdate,
    RoomMate,
    RoomMateCreate,
    RoomMatePublic,
    Split,
    SplitCreate,
    SplitUpdate,
    Transaction,
    TransactionPublic,
    TransactionUpdate,
)
from .utils import split_decimal


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI(lifespan=lifespan)


@app.post("/accounts", response_model=AccountPublic)
def create_account(
    *, session: Session = Depends(get_session), account: AccountCreate
):
    db_account = Account.model_validate(account)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@app.get("/accounts", response_model=list[AccountPublic])
def read_accounts(*, session: Session = Depends(get_session)):
    accounts = session.exec(select(Account)).all()
    return accounts


@app.get("/accounts/{account_id}", response_model=AccountPublic)
def read_account(*, session: Session = Depends(get_session), account_id: int):
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account


@app.patch("/accounts/{account_id}", response_model=AccountPublic)
def update_account(
    *,
    session: Session = Depends(get_session),
    account_id: int,
    account: AccountUpdate,
):
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_account.sqlmodel_update(account)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@app.delete("/accounts/{account_id}")
def delete_account(*, session: Session = Depends(get_session), account_id: int):
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(db_account)
    session.commit()
    return {"ok": True}


@app.get(
    "/accounts/{account_id}/transactions",
    response_model=list[TransactionPublic],
)
def read_account_transactions(
    *, session: Session = Depends(get_session), account_id: int
):
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_transactions = [split.transaction for split in db_account.splits]

    return db_transactions


@app.post(
    "/accounts/{account_id}/transactions",
    response_model=TransactionPublic,
)
def create_transaction_from_account(
    *,
    session: Session = Depends(get_session),
    account_id: int,
    splits: list[SplitCreate],
    transaction_date: date = date.today(),
    description: str | None = None,
):
    account_db = session.get(Account, account_id)
    if not account_db:
        raise HTTPException(status_code=404, detail="Account not found")

    transaction = Transaction(
        transaction_date=transaction_date, description=description, splits=[]
    )

    total: Decimal = Decimal("0")
    for split in splits:
        split_db = Split.model_validate(split)
        if not session.get(Account, split_db.account_id):
            raise HTTPException(status_code=404, detail="Account not found")
        if split_db.account_id == account_db.id:
            raise HTTPException(
                status_code=400,
                detail="Split account must be different from the transaction account",
            )
        total += split_db.amount
        transaction.splits.append(split_db)

    # add the split for the current account, to add up to zero
    transaction.splits.append(Split(account_id=account_id, amount=-total))

    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@app.patch("/transactions/{transaction_id}", response_model=TransactionPublic)
def update_transaction(
    *,
    session: Session = Depends(get_session),
    transaction_id: int,
    update: TransactionUpdate,
):
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction_data = update.model_dump(exclude_unset=True)
    db_transaction.sqlmodel_update(transaction_data)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    *,
    session: Session = Depends(get_session),
    transaction_id: int,
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    session.delete(transaction)
    session.commit()
    return {"ok": True}


@app.patch("/splits/{split_id}", response_model=TransactionPublic)
def update_split(
    *,
    session: Session = Depends(get_session),
    split_id: int,
    update: SplitUpdate,
):
    db_split = session.get(Split, split_id)
    if not db_split:
        raise HTTPException(status_code=404, detail="Split not found")
    transaction = db_split.transaction

    split_data = update.model_dump(exclude_unset=True)
    db_split.sqlmodel_update(split_data)

    session.add(db_split)
    session.commit()
    session.refresh(db_split)

    total = Decimal(sum(s.amount for s in db_split.transaction.splits))
    if total != Decimal("0.00"):
        others = [s for s in db_split.transaction.splits if s.id != db_split.id]
        match len(others):
            case 0:
                raise ValueError("Unexpected number of splits")
            case 1:
                others[0].amount -= total
            case _ if len(others) > 1:
                equal_differences = split_decimal(total, len(others))
                for i, split in enumerate(others):
                    split.amount -= equal_differences[i]

        session.add_all(others)
        session.commit()
        session.refresh(transaction)

    return transaction


@app.post("/roommates", response_model=RoomMatePublic)
def create_roommate(
    *,
    session: Session = Depends(get_session),
    roommate: RoomMateCreate,
):
    db_roommate = RoomMate.model_validate(roommate)
    roommate_account = Account(
        name=f"{db_roommate.name}_account",
        type=AccountType.ROOMMATE,
    )
    db_roommate.account = roommate_account
    session.add(db_roommate)
    session.commit()
    session.refresh(db_roommate)

    return db_roommate
