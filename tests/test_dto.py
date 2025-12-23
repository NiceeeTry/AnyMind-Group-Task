from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.application.dto.payment_dto import (
    PaymentRequest,
    PaymentResponse,
    SalesRequest,
    SalesResponse,
    HourlySales,
)
from app.domain.value_objects.payment_method import PaymentMethod


def test_create_payment_request():
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.95,
        payment_method=PaymentMethod.VISA,
        datetime="2024-01-15T10:30:00Z",
    )
    assert request.customer_id == "customer123"
    assert request.price == "100.00"
    assert request.price_modifier == 0.95
    assert request.payment_method == PaymentMethod.VISA

def test_create_payment_request_with_additional_item():
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.95,
        payment_method=PaymentMethod.VISA,
        datetime="2024-01-15T10:30:00Z",
        additional_item={"last4": "1234"},
    )
    assert request.additional_item == {"last4": "1234"}

def test_get_price_decimal():
    request = PaymentRequest(
        customer_id="customer123",
        price="100.50",
        price_modifier=1.0,
        payment_method=PaymentMethod.CASH,
        datetime="2024-01-15T10:30:00Z",
    )
    assert request.get_price_decimal() == Decimal("100.50")

def test_get_modifier_decimal():
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=0.95,
        payment_method=PaymentMethod.VISA,
        datetime="2024-01-15T10:30:00Z",
    )
    assert request.get_modifier_decimal() == Decimal("0.95")

def test_get_datetime_with_z_suffix():
    request = PaymentRequest(
        customer_id="customer123",
        price="100.00",
        price_modifier=1.0,
        payment_method=PaymentMethod.CASH,
        datetime="2024-01-15T10:30:00Z",
    )
    dt = request.get_datetime()
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 15
    assert dt.hour == 10
    assert dt.minute == 30
    assert dt.second == 0


def test_create_payment_response():
    response = PaymentResponse(
        final_price="95.00",
        points=5,
    )
    assert response.final_price == "95.00"
    assert response.points == 5


def test_create_sales_request():
    request = SalesRequest(
        start_datetime="2024-01-01T00:00:00Z",
        end_datetime="2024-01-31T23:59:59Z",
    )
    assert request.start_datetime == "2024-01-01T00:00:00Z"
    assert request.end_datetime == "2024-01-31T23:59:59Z"

def test_get_start_datetime():
    request = SalesRequest(
        start_datetime="2024-01-01T00:00:00Z",
        end_datetime="2024-01-31T23:59:59Z",
    )
    dt = request.get_start_datetime()
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 1
    assert dt.hour == 0
    assert dt.minute == 0

def test_create_hourly_sales():
    sales = HourlySales(
        datetime="2024-01-15T10:00:00Z",
        sales="500.00",
        points=25,
    )
    assert sales.datetime == "2024-01-15T10:00:00Z"
    assert sales.sales == "500.00"
    assert sales.points == 25


def test_create_sales_response():
    hourly_data = [
        HourlySales(datetime="2024-01-15T10:00:00Z", sales="500.00", points=25),
        HourlySales(datetime="2024-01-15T11:00:00Z", sales="750.00", points=40),
    ]
    response = SalesResponse(sales=hourly_data)
    assert len(response.sales) == 2
    assert response.sales[0].sales == "500.00"
    assert response.sales[1].points == 40
