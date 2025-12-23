from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from app.domain.value_objects.payment_method import PaymentMethod


@dataclass
class PaymentRequest:
    customer_id: str
    price: str
    price_modifier: float
    payment_method: PaymentMethod | str
    datetime: str
    additional_item: Optional[dict] = None
    
    def get_price_decimal(self) -> Decimal:
        """Convert price string to Decimal"""
        return Decimal(self.price)
    
    def get_modifier_decimal(self) -> Decimal:
        """Convert price modifier to Decimal"""
        return Decimal(str(self.price_modifier))
    
    def get_datetime(self) -> datetime:
        """Parse datetime string to datetime object"""
        # Handle ISO format with Z suffix as the samples in requirements were with Z suffix
        dt_str = self.datetime.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)


@dataclass
class PaymentResponse:
    final_price: str
    points: int


@dataclass
class SalesRequest:
    start_datetime: str
    end_datetime: str
    
    def get_start_datetime(self) -> datetime:
        """Parse start datetime string to datetime object"""
        dt_str = self.start_datetime.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    
    def get_end_datetime(self) -> datetime:
        """Parse end datetime string to datetime object"""
        dt_str = self.end_datetime.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)


@dataclass
class HourlySales:
    """DTO for hourly sales data"""
    
    datetime: str
    sales: str
    points: int


@dataclass
class SalesResponse:
    sales: List[HourlySales]

