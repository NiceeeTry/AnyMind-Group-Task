from typing import Optional, List
import strawberry

from app.domain.value_objects.payment_method import PaymentMethod


@strawberry.input
class AdditionalItemInput:
    """Input for additional payment item"""
    
    last4: Optional[str] = None
    courier: Optional[str] = None
    bank: Optional[str] = None
    account_number: Optional[str] = strawberry.field(default=None, name="accountNumber")
    cheque_number: Optional[str] = strawberry.field(default=None, name="chequeNumber")
    
    def to_dict(self) -> dict:
        result = {}
        if self.last4:
            result["last4"] = self.last4
        if self.courier:
            result["courier"] = self.courier
        if self.bank:
            result["bank"] = self.bank
        if self.account_number:
            result["accountNumber"] = self.account_number
        if self.cheque_number:
            result["chequeNumber"] = self.cheque_number
        return result


@strawberry.input
class PaymentInput:
    """Input for payment request"""
    
    customer_id: str = strawberry.field(name="customerId")
    price: str
    price_modifier: float = strawberry.field(name="priceModifier")
    payment_method: PaymentMethod = strawberry.field(name="paymentMethod")
    datetime: str
    additional_item: Optional[AdditionalItemInput] = strawberry.field(
        default=None, name="additionalItem"
    )


@strawberry.type
class PaymentResult:
    """Type for payment response"""
    
    final_price: str = strawberry.field(name="finalPrice")
    points: int


@strawberry.type
class ErrorDetail:
    """Type for error details"""
    
    field: str
    message: str


@strawberry.type
class PaymentError:
    """Type for payment error"""
    
    error: str
    details: Optional[List[ErrorDetail]] = None


@strawberry.input
class SalesQueryInput:
    """Input for sales query"""
    
    start_datetime: str = strawberry.field(name="startDateTime")
    end_datetime: str = strawberry.field(name="endDateTime")


@strawberry.type
class HourlySalesType:
    """Type for hourly sales data"""
    
    datetime: str
    sales: str
    points: int


@strawberry.type
class SalesReportType:
    """Type for sales report response"""
    
    sales: List[HourlySalesType]