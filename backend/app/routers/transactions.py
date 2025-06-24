from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..models import Transaction, TransactionPublic, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.patch("/{transaction_id}", response_model=TransactionPublic)
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


@router.delete("/{transaction_id}")
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
