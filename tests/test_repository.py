from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.transaction import Transaction
from app.domain.value_objects.money import Money
from app.domain.value_objects.payment_method import PaymentMethod
from app.domain.value_objects.additional_item import AdditionalItem, CourierService
from app.infrastructure.repositories.sqlalchemy_transaction_repository import (
    SqlAlchemyTransactionRepository,
)

@pytest_asyncio.fixture
async def repository(async_session: AsyncSession):
    return SqlAlchemyTransactionRepository(async_session)


def _create_transaction(
    customer_id: str = "customer123",
    price: str = "100.00",
    price_modifier: str = "0.95",
    payment_method: PaymentMethod = PaymentMethod.CASH,
    transaction_datetime: datetime = None,
    final_price: str = "95.00",
    points: int = 5,
    additional_item: AdditionalItem = None,
) -> Transaction:
    if transaction_datetime is None:
        transaction_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    
    return Transaction(
        customer_id=customer_id,
        price=Money.from_string(price),
        price_modifier=Decimal(price_modifier),
        payment_method=payment_method,
        transaction_datetime=transaction_datetime,
        final_price=Money.from_string(final_price),
        points=points,
        additional_item=additional_item,
    )

@pytest.mark.asyncio
async def test_save_transaction(repository, async_session):
    transaction = _create_transaction()

    saved = await repository.save(transaction)

    assert saved.id == transaction.id
    assert saved.customer_id == "customer123"

@pytest.mark.asyncio
async def test_save_transaction_with_additional_item(repository, async_session):
    additional_item = AdditionalItem(last4="1234")
    transaction = _create_transaction(
        payment_method=PaymentMethod.VISA,
        additional_item=additional_item,
    )

    saved = await repository.save(transaction)

    assert saved.additional_item is not None
    assert saved.additional_item.last4 == "1234"

@pytest.mark.asyncio
async def test_save_multiple_transactions(repository, async_session):
    transactions = [
        _create_transaction(customer_id="customer1"),
        _create_transaction(customer_id="customer2"),
        _create_transaction(customer_id="customer3"),
    ]

    for t in transactions:
        await repository.save(t)

    await async_session.commit()

@pytest.mark.asyncio
async def test_get_hourly_sales_single_hour(repository, async_session):
    """Test getting hourly sales for a single hour"""
    # Create transactions in the same hour
    t1 = _create_transaction(
        customer_id="c1",
        price="100.00",
        final_price="95.00",
        points=5,
        transaction_datetime=datetime(2024, 1, 15, 10, 15, 0, tzinfo=timezone.utc),
    )
    t2 = _create_transaction(
        customer_id="c2",
        price="200.00",
        final_price="190.00",
        points=10,
        transaction_datetime=datetime(2024, 1, 15, 10, 45, 0, tzinfo=timezone.utc),
    )

    await repository.save(t1)
    await repository.save(t2)
    await async_session.commit()

    result = await repository.get_hourly_sales(
        start_datetime=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        end_datetime=datetime(2024, 1, 15, 23, 59, 59, tzinfo=timezone.utc),
    )

    assert len(result) == 1
    assert result[0]["sales"] == Decimal("285.00")  # 95 + 190
    assert result[0]["points"] == 15  # 5 + 10

@pytest.mark.asyncio
async def test_get_hourly_sales_multiple_hours(repository, async_session):
    # Create transactions in different hours
    t1 = _create_transaction(
        customer_id="c1",
        final_price="100.00",
        points=5,
        transaction_datetime=datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
    )
    t2 = _create_transaction(
        customer_id="c2",
        final_price="200.00",
        points=10,
        transaction_datetime=datetime(2024, 1, 15, 11, 0, 0, tzinfo=timezone.utc),
    )
    t3 = _create_transaction(
        customer_id="c3",
        final_price="300.00",
        points=15,
        transaction_datetime=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )

    await repository.save(t1)
    await repository.save(t2)
    await repository.save(t3)
    await async_session.commit()

    result = await repository.get_hourly_sales(
        start_datetime=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        end_datetime=datetime(2024, 1, 15, 23, 59, 59, tzinfo=timezone.utc),
    )

    assert len(result) == 3

@pytest.mark.asyncio
async def test_get_hourly_sales_empty_range(repository, async_session):
    # Create a transaction outside the query range
    t = _create_transaction(
        transaction_datetime=datetime(2024, 1, 10, 10, 0, 0, tzinfo=timezone.utc),
    )
    await repository.save(t)
    await async_session.commit()

    result = await repository.get_hourly_sales(
        start_datetime=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        end_datetime=datetime(2024, 1, 15, 23, 59, 59, tzinfo=timezone.utc),
    )

    assert len(result) == 0

@pytest.mark.asyncio
async def test_get_hourly_sales_filters_by_date_range(repository, async_session):
    # Create transactions: 2 in range, 1 outside
    t1 = _create_transaction(
        customer_id="c1",
        final_price="100.00",
        transaction_datetime=datetime(2024, 1, 14, 10, 0, 0, tzinfo=timezone.utc),
    )
    t2 = _create_transaction(
        customer_id="c2",
        final_price="200.00",
        transaction_datetime=datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
    )
    t3 = _create_transaction(
        customer_id="c3",
        final_price="300.00",
        transaction_datetime=datetime(2024, 1, 16, 10, 0, 0, tzinfo=timezone.utc),
    )

    await repository.save(t1)
    await repository.save(t2)
    await repository.save(t3)
    await async_session.commit()

    result = await repository.get_hourly_sales(
        start_datetime=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        end_datetime=datetime(2024, 1, 15, 23, 59, 59, tzinfo=timezone.utc),
    )

    # Only t2 should be in the result
    assert len(result) == 1
    assert result[0]["sales"] == Decimal("200.00")

@pytest.mark.asyncio
async def test_get_hourly_sales_ordered_by_hour(repository, async_session):
    # Create transactions in reverse order
    t1 = _create_transaction(
        customer_id="c1",
        final_price="100.00",
        transaction_datetime=datetime(2024, 1, 15, 14, 0, 0, tzinfo=timezone.utc),
    )
    t2 = _create_transaction(
        customer_id="c2",
        final_price="200.00",
        transaction_datetime=datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
    )
    t3 = _create_transaction(
        customer_id="c3",
        final_price="300.00",
        transaction_datetime=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )

    await repository.save(t1)
    await repository.save(t2)
    await repository.save(t3)
    await async_session.commit()

    result = await repository.get_hourly_sales(
        start_datetime=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        end_datetime=datetime(2024, 1, 15, 23, 59, 59, tzinfo=timezone.utc),
    )

    assert len(result) == 3
    # Should be ordered by hour: 10, 12, 14
    def get_hour(dt):
        if isinstance(dt, str):
            return datetime.fromisoformat(dt.replace("Z", "+00:00")).hour
        return dt.hour
    
    assert get_hour(result[0]["datetime"]) == 10
    assert get_hour(result[1]["datetime"]) == 12
    assert get_hour(result[2]["datetime"]) == 14


@pytest.mark.asyncio
async def test_to_model_preserves_all_fields(repository, async_session):
    transaction_id = uuid4()
    additional_item = AdditionalItem(
        last4="1234",
        courier=CourierService.YAMATO,
        bank="Test Bank",
        account_number="123456",
        cheque_number="CHQ001",
    )
    transaction = Transaction(
        id=transaction_id,
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("0.95"),
        payment_method=PaymentMethod.VISA,
        transaction_datetime=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        final_price=Money.from_string("95.00"),
        points=3,
        additional_item=additional_item,
    )

    model = repository._to_model(transaction)

    assert model.id == transaction_id
    assert model.customer_id == "customer123"
    assert model.price == Decimal("100.00")
    assert model.price_modifier == Decimal("0.95")
    assert model.payment_method == "VISA"
    assert model.final_price == Decimal("95.00")
    assert model.points == 3
    assert model.additional_item is not None
    assert model.additional_item["last4"] == "1234"

