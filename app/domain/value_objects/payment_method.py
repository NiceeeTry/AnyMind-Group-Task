from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

import strawberry


@strawberry.enum
class PaymentMethod(str, Enum):
    """Supported payment methods in the system"""
    
    CASH = "CASH"
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMEX = "AMEX"
    JCB = "JCB"
    LINE_PAY = "LINE_PAY"
    PAYPAY = "PAYPAY"
    POINTS = "POINTS"
    GRAB_PAY = "GRAB_PAY"
    BANK_TRANSFER = "BANK_TRANSFER"
    CHEQUE = "CHEQUE"


@dataclass(frozen=True)
class PaymentMethodConfig:
    """Configuration for a payment method including price modifier range and point rate"""
    
    method: PaymentMethod
    min_price_modifier: Decimal
    max_price_modifier: Decimal
    point_rate: Decimal
    requires_last4: bool = False
    requires_courier: bool = False
    requires_bank_info: bool = False
    requires_cheque_info: bool = False
    
    def is_valid_price_modifier(self, modifier: Decimal) -> bool:
        """Check if the price modifier is within the allowed range"""
        return self.min_price_modifier <= modifier <= self.max_price_modifier
    
    def calculate_points(self, price: Decimal) -> int:
        """Calculate points earned for a given price"""
        points = price * self.point_rate
        return int(points)


PAYMENT_METHOD_CONFIGS: dict[PaymentMethod, PaymentMethodConfig] = {
    PaymentMethod.CASH: PaymentMethodConfig(
        method=PaymentMethod.CASH,
        min_price_modifier=Decimal("0.9"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.05"),
    ),
    PaymentMethod.CASH_ON_DELIVERY: PaymentMethodConfig(
        method=PaymentMethod.CASH_ON_DELIVERY,
        min_price_modifier=Decimal("1.0"),
        max_price_modifier=Decimal("1.02"),
        point_rate=Decimal("0.05"),
        requires_courier=True,
    ),
    PaymentMethod.VISA: PaymentMethodConfig(
        method=PaymentMethod.VISA,
        min_price_modifier=Decimal("0.95"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.03"),
        requires_last4=True,
    ),
    PaymentMethod.MASTERCARD: PaymentMethodConfig(
        method=PaymentMethod.MASTERCARD,
        min_price_modifier=Decimal("0.95"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.03"),
        requires_last4=True,
    ),
    PaymentMethod.AMEX: PaymentMethodConfig(
        method=PaymentMethod.AMEX,
        min_price_modifier=Decimal("0.98"),
        max_price_modifier=Decimal("1.01"),
        point_rate=Decimal("0.02"),
        requires_last4=True,
    ),
    PaymentMethod.JCB: PaymentMethodConfig(
        method=PaymentMethod.JCB,
        min_price_modifier=Decimal("0.95"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.05"),
        requires_last4=True,
    ),
    PaymentMethod.LINE_PAY: PaymentMethodConfig(
        method=PaymentMethod.LINE_PAY,
        min_price_modifier=Decimal("1.0"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.01"),
    ),
    PaymentMethod.PAYPAY: PaymentMethodConfig(
        method=PaymentMethod.PAYPAY,
        min_price_modifier=Decimal("1.0"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.01"),
    ),
    PaymentMethod.POINTS: PaymentMethodConfig(
        method=PaymentMethod.POINTS,
        min_price_modifier=Decimal("1.0"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.0"),
    ),
    PaymentMethod.GRAB_PAY: PaymentMethodConfig(
        method=PaymentMethod.GRAB_PAY,
        min_price_modifier=Decimal("1.0"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.01"),
    ),
    PaymentMethod.BANK_TRANSFER: PaymentMethodConfig(
        method=PaymentMethod.BANK_TRANSFER,
        min_price_modifier=Decimal("1.0"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.0"),
        requires_bank_info=True,
    ),
    PaymentMethod.CHEQUE: PaymentMethodConfig(
        method=PaymentMethod.CHEQUE,
        min_price_modifier=Decimal("0.9"),
        max_price_modifier=Decimal("1.0"),
        point_rate=Decimal("0.0"),
        requires_cheque_info=True,
    ),
}


def get_payment_config(method: PaymentMethod) -> PaymentMethodConfig:
    """Get the configuration for a payment method"""
    return PAYMENT_METHOD_CONFIGS[method]

