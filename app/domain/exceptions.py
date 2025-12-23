from typing import List


class DomainException(Exception):
    """Base exception for domain errors"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationException(DomainException):
    """Exception for validation errors"""
    
    def __init__(self, errors: List[dict]):
        self.errors = errors
        message = "; ".join([f"{e['field']}: {e['message']}" for e in errors])
        super().__init__(message)


class PaymentMethodNotSupportedException(DomainException):
    """Exception when an unsupported payment method is used"""
    
    def __init__(self, method: str):
        super().__init__(f"Payment method '{method}' is not supported")


class InvalidPriceException(DomainException):
    """Exception for invalid price values"""
    
    def __init__(self, message: str = "Invalid price value"):
        super().__init__(message)

