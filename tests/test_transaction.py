from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities.transaction import Transaction
from app.domain.value_objects.money import Money
from app.domain.value_objects.payment_method import PaymentMethod
from app.domain.value_objects.additional_item import AdditionalItem, CourierService


def test_create_transaction():
    transaction = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("0.95"),
        payment_method=PaymentMethod.VISA,
        transaction_datetime=datetime(2024, 1, 15, 10, 30, 0),
        final_price=Money.from_string("95.00"),
        points=3,
    )
    
    assert transaction.customer_id == "customer123"
    assert transaction.price.amount == Decimal("100.00")
    assert transaction.price_modifier == Decimal("0.95")
    assert transaction.payment_method == PaymentMethod.VISA
    assert transaction.final_price.amount == Decimal("95.00")
    assert transaction.points == 3
    assert transaction.additional_item is None
    assert transaction.id is not None
    assert transaction.created_at is not None

def test_create_transaction_with_additional_item():
    additional_item = AdditionalItem(last4="1234")
    transaction = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("0.95"),
        payment_method=PaymentMethod.VISA,
        transaction_datetime=datetime(2024, 1, 15, 10, 30, 0),
        final_price=Money.from_string("95.00"),
        points=3,
        additional_item=additional_item,
    )
    
    assert transaction.additional_item is not None
    assert transaction.additional_item.last4 == "1234"

def test_create_transaction_with_custom_id():
    custom_id = uuid4()
    transaction = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.CASH,
        transaction_datetime=datetime(2024, 1, 15, 10, 30, 0),
        final_price=Money.from_string("100.00"),
        points=5,
        id=custom_id,
    )
    
    assert transaction.id == custom_id


def test_hour_bucket_truncates_minutes():
    transaction = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.CASH,
        transaction_datetime=datetime(2024, 1, 15, 10, 45, 30),
        final_price=Money.from_string("100.00"),
        points=5,
    )
    
    assert transaction.hour_bucket == datetime(2024, 1, 15, 10, 0, 0)

def test_hour_bucket_preserves_hour():
    transaction = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.CASH,
        transaction_datetime=datetime(2024, 1, 15, 23, 59, 59),
        final_price=Money.from_string("100.00"),
        points=5,
    )
    
    assert transaction.hour_bucket == datetime(2024, 1, 15, 23, 0, 0)

def test_hour_bucket_at_exact_hour():
    transaction = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.CASH,
        transaction_datetime=datetime(2024, 1, 15, 14, 0, 0),
        final_price=Money.from_string("100.00"),
        points=5,
    )
    
    assert transaction.hour_bucket == datetime(2024, 1, 15, 14, 0, 0)


def test_transactions_equal_by_id():
    shared_id = uuid4()
    transaction1 = Transaction(
        customer_id="customer1",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.CASH,
        transaction_datetime=datetime(2024, 1, 15, 10, 0, 0),
        final_price=Money.from_string("100.00"),
        points=5,
        id=shared_id,
    )
    transaction2 = Transaction(
        customer_id="customer2",
        price=Money.from_string("200.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.VISA,
        transaction_datetime=datetime(2024, 1, 16, 10, 0, 0),
        final_price=Money.from_string("200.00"),
        points=6,
        id=shared_id,
    )
    
    assert transaction1 == transaction2

def test_transactions_not_equal_different_id():
    transaction1 = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.CASH,
        transaction_datetime=datetime(2024, 1, 15, 10, 0, 0),
        final_price=Money.from_string("100.00"),
        points=5,
    )
    transaction2 = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.CASH,
        transaction_datetime=datetime(2024, 1, 15, 10, 0, 0),
        final_price=Money.from_string("100.00"),
        points=5,
    )
    
    assert transaction1 != transaction2

def test_transaction_not_equal_to_non_transaction():
    transaction = Transaction(
        customer_id="customer123",
        price=Money.from_string("100.00"),
        price_modifier=Decimal("1.0"),
        payment_method=PaymentMethod.CASH,
        transaction_datetime=datetime(2024, 1, 15, 10, 0, 0),
        final_price=Money.from_string("100.00"),
        points=5,
    )
    
    assert transaction != "not a transaction"
    assert transaction != 123
    assert transaction != None
