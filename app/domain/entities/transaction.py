from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from app.domain.value_objects.payment_method import PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.value_objects.additional_item import AdditionalItem


@dataclass
class Transaction:
    """Entity representing a payment transaction"""
    
    customer_id: str
    price: Money
    price_modifier: Decimal
    payment_method: PaymentMethod
    transaction_datetime: datetime
    final_price: Money
    points: int
    additional_item: Optional[AdditionalItem] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def hour_bucket(self) -> datetime:
        """Get the hourly bucket for this transaction"""
        return self.transaction_datetime.replace(
            minute=0, second=0, microsecond=0
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return False
        return self.id == other.id

