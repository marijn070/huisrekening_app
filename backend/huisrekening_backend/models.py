from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
)


class TransactionBase(SQLModel):
    description: str | None = None
    transaction_date: date = Field(default_factory=date.today)


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    splits: list["Split"] = Relationship(
        back_populates="transaction", cascade_delete=True
    )


class TransactionUpdate(TransactionBase):
    pass


class TransactionPublic(TransactionBase):
    id: int
    splits: list["SplitPublic"]


class SplitBase(SQLModel):
    amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    description: str | None = None
    account_id: int = Field(foreign_key="account.id", ondelete="RESTRICT")


class Split(SplitBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    transaction_id: int | None = Field(
        default=None, foreign_key="transaction.id", ondelete="CASCADE"
    )
    transaction: Transaction = Relationship(back_populates="splits")
    account: "Account" = Relationship(back_populates="splits")


class SplitCreate(SplitBase):
    pass


class SplitUpdate(SplitBase):
    account_id: int | None = None


class SplitPublic(SplitBase):
    id: int
    transaction_id: int
    account_id: int


class AccountType(str, Enum):
    BANK = "bank"
    ROOMMATE = "roommate"
    EXPENSE = "expense"
    RENT = "rent"


class AccountBase(SQLModel):
    name: str = Field(max_length=100)
    type: AccountType


class Account(AccountBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    splits: list["Split"] = Relationship(
        back_populates="account", passive_deletes="all"
    )

    room_mate: Optional["RoomMate"] = Relationship(back_populates="account")


class AccountCreate(AccountBase):
    pass


class AccountUpdate(AccountBase):
    pass


class AccountPublic(AccountBase):
    id: int


class AccountPublicWithTransactions(AccountPublic):
    transactions: list[TransactionPublic] = []


class RoomMateBase(SQLModel):
    name: str
    email: str | None = Field(default=None, max_length=100)
    profile_pic_url: str | None = Field(default=None, max_length=200)


class RoomMate(RoomMateBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    account_id: int | None = Field(default=None, foreign_key="account.id")
    account: Account = Relationship(back_populates="room_mate")


class RoomMateCreate(RoomMateBase):
    pass


class RoomMatePublic(RoomMateBase):
    id: int
    account: AccountPublic


class Room(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    prices: list["RoomPrice"] = Relationship(
        back_populates="room", passive_deletes="all"
    )
    occupancies: list["Occupancy"] = Relationship(
        back_populates="room", passive_deletes="all"
    )


class RoomPrice(SQLModel, table=True):
    room_id: int = Field(
        foreign_key="room.id", primary_key=True, ondelete="RESTRICT"
    )
    month: date = Field(primary_key=True)
    price: Decimal = Field(default=0, max_digits=10, decimal_places=2)

    room: Room = Relationship(back_populates="prices")


class Occupancy(SQLModel, table=True):
    start_date: date = Field(primary_key=True)
    end_date: date | None = Field(default=None)
    room_id: int = Field(
        foreign_key="room.id", primary_key=True, ondelete="RESTRICT"
    )
    room: Room = Relationship(back_populates="occupancies")
