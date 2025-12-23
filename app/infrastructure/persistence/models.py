from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    String,
    Numeric,
    DateTime,
    Integer,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database import Base


class TransactionModel(Base):
    """SQLAlchemy model for transactions"""
    
    __tablename__ = "transactions"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
    )
    customer_id: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_modifier: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    transaction_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    final_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    additional_item: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Index for efficient querying
    __table_args__ = (
        Index("ix_transactions_datetime", "transaction_datetime"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, "
            f"customer_id={self.customer_id}, "
            f"final_price={self.final_price})>"
        )

