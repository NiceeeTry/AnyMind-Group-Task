from decimal import InvalidOperation

from app.domain.entities.transaction import Transaction
from app.domain.repositories.transaction_repository import TransactionRepository
from app.domain.services.payment_service import PaymentService
from app.domain.value_objects.payment_method import PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.value_objects.additional_item import AdditionalItem
from app.domain.exceptions import (
    ValidationException,
    PaymentMethodNotSupportedException,
    InvalidPriceException,
)
from app.application.dto.payment_dto import PaymentRequest, PaymentResponse


class ProcessPaymentUseCase:
    """Use case for processing a payment"""
    
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        payment_service: PaymentService,
    ):
        self._transaction_repository = transaction_repository
        self._payment_service = payment_service
    
    async def execute(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process a payment request
        
        Args:
            request: Payment request DTO
            
        Returns:
            Payment response with final price and points
            
        Raises:
            ValidationException: If request validation fails
            PaymentMethodNotSupportedException: If payment method is invalid
            InvalidPriceException: If price is invalid
        """
        # Parse and validate payment method
        try:
            payment_method = PaymentMethod(request.payment_method)
        except ValueError:
            raise PaymentMethodNotSupportedException(request.payment_method)
        
        # Parse and validate price
        try:
            price = Money.from_string(request.price)
        except (InvalidOperation, ValueError):
            raise InvalidPriceException(f"Invalid price format: {request.price}")
        
        # Parse price modifier
        try:
            price_modifier = request.get_modifier_decimal()
        except (InvalidOperation, ValueError):
            raise InvalidPriceException("Invalid price modifier format")
        
        # Parse additional item
        additional_item = AdditionalItem.from_dict(request.additional_item)
        
        # Validate payment against business rules
        validation_errors = self._payment_service.validate_payment(
            payment_method=payment_method,
            price_modifier=price_modifier,
            additional_item=additional_item,
        )
        
        if validation_errors:
            raise ValidationException([
                {"field": e.field, "message": e.message}
                for e in validation_errors
            ])

        final_price = self._payment_service.calculate_final_price(price, price_modifier)
        points = self._payment_service.calculate_points(price, payment_method)

        transaction = Transaction(
            customer_id=request.customer_id,
            price=price,
            price_modifier=price_modifier,
            payment_method=payment_method,
            transaction_datetime=request.get_datetime(),
            final_price=final_price,
            points=points,
            additional_item=additional_item,
        )
        
        await self._transaction_repository.save(transaction)
        
        return PaymentResponse(
            final_price=final_price.to_string(),
            points=points,
        )

