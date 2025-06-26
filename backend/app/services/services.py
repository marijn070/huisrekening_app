from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import Session

from ..models import Account, RoomMate, Split, SplitCreate, Transaction


def sync_roommate_account_name(session: Session, roommate: RoomMate) -> None:
    roommate_account = roommate.account
    if roommate_account is not None:
        roommate_account.name = f"{roommate.name}_account"
        session.add(roommate_account)
        session.commit()
        session.refresh(roommate_account)


def compute_balance(session: Session, account: Account) -> Decimal:
    balance = Decimal("0.00")
    for split in account.splits:
        balance += split.amount
    return balance


def create_transaction_with_known_account_from_splits(
    session: Session,
    account: Account,
    splits: list[SplitCreate],
    transaction_date: date = date.today(),
    description: str | None = None,
):
    transaction = Transaction(
        transaction_date=transaction_date, description=description, splits=[]
    )

    total: Decimal = Decimal("0.00")
    for split in splits:
        split_db = Split.model_validate(split)
        if not session.get(Account, split_db.account_id):
            raise HTTPException(
                status_code=404,
                detail="Account for one of the entered split not found",
            )
        if split_db.account_id == account.id:
            raise HTTPException(
                status_code=400,
                detail="Split account must be different from the transaction account",
            )
        total += split_db.amount
        transaction.splits.append(split_db)

    # add the split for the current account, to add up to zero
    balancing_split = Split(amount=-total)
    account.splits.append(balancing_split)
    transaction.splits.append(balancing_split)

    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction
