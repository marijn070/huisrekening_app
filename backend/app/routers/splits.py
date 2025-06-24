from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..models import Split, SplitUpdate, TransactionPublic
from ..utils import split_decimal

router = APIRouter(prefix="/splits", tags=["splits"])


@router.patch("/{split_id}", response_model=TransactionPublic)
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
