from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import (
    Account,
    AccountCreate,
    AccountPublic,
    AccountUpdate,
    Split,
    SplitCreate,
    Transaction,
    TransactionPublic,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountPublic)
def create_account(
    *, session: Session = Depends(get_session), account: AccountCreate
):
    db_account = Account.model_validate(account)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@router.get("", response_model=list[AccountPublic])
def read_accounts(*, session: Session = Depends(get_session)):
    accounts = session.exec(select(Account)).all()
    return accounts


@router.get("/{account_id}", response_model=AccountPublic)
def read_account(*, session: Session = Depends(get_session), account_id: int):
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account


@router.patch("/{account_id}", response_model=AccountPublic)
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


@router.delete("/{account_id}")
def delete_account(*, session: Session = Depends(get_session), account_id: int):
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(db_account)
    session.commit()
    return {"ok": True}


@router.post(
    "/{account_id}/transactions",
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


@router.get(
    "/{account_id}/transactions",
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
