from typing import Union

from app.application.dto.payment_dto import PaymentRequest, SalesRequest
from app.application.use_cases.process_payment import ProcessPaymentUseCase
from app.application.use_cases.get_sales_report import GetSalesReportUseCase
from app.domain.services.payment_service import PaymentService
from app.domain.exceptions import (
    ValidationException,
    PaymentMethodNotSupportedException,
    InvalidPriceException,
)
from app.infrastructure.repositories.sqlalchemy_transaction_repository import (
    SqlAlchemyTransactionRepository,
)
from app.infrastructure.persistence.database import get_session_context
from app.presentation.graphql.types import (
    PaymentInput,
    PaymentResult,
    PaymentError,
    ErrorDetail,
    SalesQueryInput,
    SalesReportType,
    HourlySalesType,
)


async def process_payment(
    input: PaymentInput,
) -> Union[PaymentResult, PaymentError]:
    """Process a payment mutation resolver"""
    try:
        async with get_session_context() as session:
            repository = SqlAlchemyTransactionRepository(session)
            payment_service = PaymentService()
            use_case = ProcessPaymentUseCase(repository, payment_service)
            
            request = PaymentRequest(
                customer_id=input.customer_id,
                price=input.price,
                price_modifier=input.price_modifier,
                payment_method=input.payment_method,
                datetime=input.datetime,
                additional_item=input.additional_item.to_dict() if input.additional_item else None,
            )
            
            response = await use_case.execute(request)
            
            return PaymentResult(
                final_price=response.final_price,
                points=response.points,
            )
    
    except ValidationException as e:
        return PaymentError(
            error="Validation failed",
            details=[
                ErrorDetail(field=err["field"], message=err["message"])
                for err in e.errors
            ],
        )
    
    except PaymentMethodNotSupportedException as e:
        return PaymentError(error=e.message)
    
    except InvalidPriceException as e:
        return PaymentError(error=e.message)
    
    except Exception as e:
        return PaymentError(error=f"An unexpected error occurred: {str(e)}")


async def get_sales_report(input: SalesQueryInput) -> SalesReportType:
    """Get sales report query resolver"""
    async with get_session_context() as session:
        repository = SqlAlchemyTransactionRepository(session)
        use_case = GetSalesReportUseCase(repository)
        
        request = SalesRequest(
            start_datetime=input.start_datetime,
            end_datetime=input.end_datetime,
        )
        
        response = await use_case.execute(request)
        
        return SalesReportType(
            sales=[
                HourlySalesType(
                    datetime=hour.datetime,
                    sales=hour.sales,
                    points=hour.points,
                )
                for hour in response.sales
            ]
        )

