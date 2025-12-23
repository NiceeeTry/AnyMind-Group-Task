from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from app.application.dto.payment_dto import PaymentRequest, SalesRequest
from app.application.use_cases.process_payment import ProcessPaymentUseCase
from app.application.use_cases.get_sales_report import GetSalesReportUseCase
from app.domain.entities.transaction import Transaction
from app.domain.exceptions import (
    ValidationException,
    PaymentMethodNotSupportedException,
    InvalidPriceException,
)
from app.domain.services.payment_service import PaymentService
from app.domain.value_objects.money import Money
from app.domain.value_objects.payment_method import PaymentMethod


@pytest.fixture
def mock_repository():
    repository = AsyncMock()
    repository.save = AsyncMock(side_effect=lambda t: t)
    return repository

@pytest.fixture
def payment_service():
    return PaymentService()

@pytest.fixture
def payment_use_case(mock_repository, payment_service):
    return ProcessPaymentUseCase(mock_repository, payment_service)

@pytest.fixture
def sales_use_case(mock_repository):
    return GetSalesReportUseCase(mock_repository)

@pytest.mark.asyncio
async def test_process_cash_payment_success(payment_use_case, mock_repository):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.95,
        payment_method=PaymentMethod.CASH,
        datetime="2024-01-15T10:30:00Z",
    )

    response = await payment_use_case.execute(request)

    assert response.final_price == "95.00"
    assert response.points == 5  # 5% of 100
    mock_repository.save.assert_called_once()

@pytest.mark.asyncio
async def test_process_visa_payment_success(payment_use_case, mock_repository):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.98,
        payment_method=PaymentMethod.VISA,
        datetime="2024-01-15T10:30:00Z",
        additional_item={"last4": "1234"},
    )

    response = await payment_use_case.execute(request)

    assert response.final_price == "98.00"
    assert response.points == 3
    mock_repository.save.assert_called_once()

@pytest.mark.asyncio
async def test_process_payment_with_string_payment_method(payment_use_case, mock_repository):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.95,
        payment_method="CASH",
        datetime="2024-01-15T10:30:00Z",
    )

    response = await payment_use_case.execute(request)

    assert response.final_price == "95.00"
    mock_repository.save.assert_called_once()

@pytest.mark.asyncio
async def test_process_payment_invalid_method_raises_exception(payment_use_case):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=1.0,
        payment_method="INVALID",
        datetime="2024-01-15T10:30:00Z",
    )

    with pytest.raises(PaymentMethodNotSupportedException):
        await payment_use_case.execute(request)

@pytest.mark.asyncio
async def test_process_payment_invalid_price_raises_exception(payment_use_case):
    request = PaymentRequest(
        customer_id="customer123",
        price="not_a_price",
        price_modifier=1.0,
        payment_method="CASH",
        datetime="2024-01-15T10:30:00Z",
    )

    with pytest.raises(InvalidPriceException):
        await payment_use_case.execute(request)


@pytest.mark.asyncio
async def test_process_visa_payment_missing_last4_raises_validation_error(payment_use_case):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.95,
        payment_method="VISA",
        datetime="2024-01-15T10:30:00Z",
    )

    with pytest.raises(ValidationException) as exc_info:
        await payment_use_case.execute(request)
    
    assert any(e["field"] == "additionalItem.last4" for e in exc_info.value.errors)

@pytest.mark.asyncio
async def test_process_cash_on_delivery_with_courier(payment_use_case, mock_repository):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=1.0,
        payment_method="CASH_ON_DELIVERY",
        datetime="2024-01-15T10:30:00Z",
        additional_item={"courier": "YAMATO"},
    )

    response = await payment_use_case.execute(request)

    assert response.final_price == "100.00"
    assert response.points == 5  # 5% of 100
    mock_repository.save.assert_called_once()

@pytest.mark.asyncio
async def test_process_bank_transfer_with_bank_info(payment_use_case, mock_repository):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=1.0,
        payment_method="BANK_TRANSFER",
        datetime="2024-01-15T10:30:00Z",
        additional_item={"bank": "Test Bank", "accountNumber": "123456"},
    )

    response = await payment_use_case.execute(request)

    assert response.final_price == "100.00"
    assert response.points == 0  # No points for bank transfer
    mock_repository.save.assert_called_once()

@pytest.mark.asyncio
async def test_process_cheque_payment(payment_use_case, mock_repository):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.95,
        payment_method="CHEQUE",
        datetime="2024-01-15T10:30:00Z",
        additional_item={"bank": "Test Bank", "chequeNumber": "CHQ001"},
    )

    response = await payment_use_case.execute(request)

    assert response.final_price == "95.00"
    assert response.points == 0  # No points for cheque
    mock_repository.save.assert_called_once()

@pytest.mark.asyncio
async def test_transaction_saved_with_correct_data(payment_use_case, mock_repository):
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.95,
        payment_method=PaymentMethod.CASH,
        datetime="2024-01-15T10:30:00Z",
    )

    await payment_use_case.execute(request)

    mock_repository.save.assert_called_once()
    saved_transaction = mock_repository.save.call_args[0][0]
    
    assert isinstance(saved_transaction, Transaction)
    assert saved_transaction.customer_id == "customer123"
    assert saved_transaction.price.amount == Decimal("100.00")
    assert saved_transaction.price_modifier == Decimal("0.95")
    assert saved_transaction.payment_method == PaymentMethod.CASH
    assert saved_transaction.final_price.amount == Decimal("95.00")
    assert saved_transaction.points == 5


@pytest.mark.asyncio
async def test_get_sales_report_success(sales_use_case, mock_repository):
    mock_repository.get_hourly_sales.return_value = [
        {
            "datetime": datetime(2024, 1, 15, 10, 0, 0),
            "sales": Decimal("500.00"),
            "points": 25,
        },
        {
            "datetime": datetime(2024, 1, 15, 11, 0, 0),
            "sales": Decimal("750.00"),
            "points": 40,
        },
    ]

    request = SalesRequest(
        start_datetime="2024-01-15T00:00:00Z",
        end_datetime="2024-01-15T23:59:59Z",
    )

    response = await sales_use_case.execute(request)

    assert len(response.sales) == 2
    assert response.sales[0].datetime == "2024-01-15T10:00:00Z"
    assert response.sales[0].sales == "500.00"
    assert response.sales[0].points == 25
    assert response.sales[1].datetime == "2024-01-15T11:00:00Z"
    assert response.sales[1].sales == "750.00"
    assert response.sales[1].points == 40


@pytest.mark.asyncio
async def test_get_sales_report_empty(sales_use_case, mock_repository):
    """Test getting an empty sales report"""
    mock_repository.get_hourly_sales.return_value = []

    request = SalesRequest(
        start_datetime="2024-01-15T00:00:00Z",
        end_datetime="2024-01-15T23:59:59Z",
    )

    response = await sales_use_case.execute(request)

    assert len(response.sales) == 0


@pytest.mark.asyncio
async def test_get_sales_report_calls_repository_with_correct_dates(
    sales_use_case, mock_repository
):
    mock_repository.get_hourly_sales.return_value = []

    request = SalesRequest(
        start_datetime="2024-01-01T00:00:00Z",
        end_datetime="2024-01-31T23:59:59Z",
    )

    await sales_use_case.execute(request)

    mock_repository.get_hourly_sales.assert_called_once()
    call_args = mock_repository.get_hourly_sales.call_args
    start_dt = call_args.kwargs["start_datetime"]
    end_dt = call_args.kwargs["end_datetime"]
    
    assert start_dt.year == 2024
    assert start_dt.month == 1
    assert start_dt.day == 1
    assert end_dt.year == 2024
    assert end_dt.month == 1
    assert end_dt.day == 31

