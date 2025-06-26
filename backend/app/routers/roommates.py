from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import (
    Account,
    AccountType,
    RoomMate,
    RoomMateCreate,
    RoomMatePublic,
    RoomMateUpdate,
)

router = APIRouter(prefix="/roommates", tags=["roommates"])


@router.post("", response_model=RoomMatePublic)
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


@router.get("", response_model=list[RoomMatePublic])
def read_roommates(
    *,
    session: Session = Depends(get_session),
):
    db_roommates = session.exec(select(RoomMate)).all()
    return db_roommates


@router.get("/{roommate_id}", response_model=RoomMatePublic)
def read_roommate(
    *,
    session: Session = Depends(get_session),
    roommate_id: int,
):
    db_roommate = session.get(RoomMate, roommate_id)
    if not db_roommate:
        raise HTTPException(status_code=404, detail="Roommate not found")
    return db_roommate


@router.patch("/{roommate_id}", response_model=RoomMatePublic)
def update_roommate(
    *,
    session: Session = Depends(get_session),
    roommate_id: int,
    roommate: RoomMateUpdate,
):
    db_roommate = session.get(RoomMate, roommate_id)
    if not db_roommate:
        raise HTTPException(status_code=404, detail="Roommate not found")
    update_data = roommate.model_dump(exclude_unset=True)
    if update_data.get("name"):
        if db_roommate.account:
            db_roommate.account.name = f"{update_data['name']}_account"

    db_roommate.sqlmodel_update(update_data)
    session.add(db_roommate)
    session.commit()
    session.refresh(db_roommate)

    return db_roommate


@router.delete("/{roommate_id}")
def delete_roommate(
    *,
    session: Session = Depends(get_session),
    roommate_id: int,
):
    db_roommate = session.get(RoomMate, roommate_id)
    if not db_roommate:
        raise HTTPException(status_code=404, detail="Roommate not found")
    # try to delete the roommates account
    if db_roommate.account:
        try:
            session.delete(db_roommate.account)
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete roommate account, maybe there are still transactions in it: {e}",
            )
    session.delete(db_roommate)
    session.commit()

    return {"ok": True}
