from dataclasses import dataclass
from decimal import Decimal
from typing import List

from app.domain.value_objects.payment_method import (
    PaymentMethod,
    get_payment_config,
)
from app.domain.value_objects.money import Money
from app.domain.value_objects.additional_item import AdditionalItem, CourierService


@dataclass
class ValidationError:   
    field: str
    message: str


class PaymentService:
    """Domain service for payment processing and validation"""
    
    def validate_payment(
        self,
        payment_method: PaymentMethod,
        price_modifier: Decimal,
        additional_item: AdditionalItem | None,
    ) -> List[ValidationError]:
        errors: List[ValidationError] = []
        config = get_payment_config(payment_method)
        
        # Validate price modifier range
        if not config.is_valid_price_modifier(price_modifier):
            errors.append(ValidationError(
                field="priceModifier",
                message=f"Price modifier must be between {config.min_price_modifier} "
                        f"and {config.max_price_modifier} for {payment_method.value}"
            ))
        
        # Validate additional items based on payment method
        if additional_item is None:
            additional_item = AdditionalItem()
        
        if config.requires_last4 and not additional_item.validate_last4():
            errors.append(ValidationError(
                field="additionalItem.last4",
                message="Card last 4 digits are required and must be exactly 4 digits"
            ))
        
        if config.requires_courier:
            if not additional_item.validate_courier():
                errors.append(ValidationError(
                    field="additionalItem.courier",
                    message=f"Courier service is required. "
                            f"Allowed values: {[c.value for c in CourierService]}"
                ))
        
        if config.requires_bank_info and not additional_item.validate_bank_info():
            errors.append(ValidationError(
                field="additionalItem",
                message="Bank name and account number are required for bank transfer"
            ))
        
        if config.requires_cheque_info and not additional_item.validate_cheque_info():
            errors.append(ValidationError(
                field="additionalItem",
                message="Bank name and cheque number are required for cheque payment"
            ))
        
        return errors
    
    def calculate_final_price(
        self,
        price: Money,
        price_modifier: Decimal,
    ) -> Money:
        """Calculate the final price after applying the modifier"""
        return price.apply_modifier(price_modifier)
    
    def calculate_points(
        self,
        price: Money,
        payment_method: PaymentMethod,
    ) -> int:
        """Calculate points earned based on payment method"""
        config = get_payment_config(payment_method)
        return config.calculate_points(price.amount)

