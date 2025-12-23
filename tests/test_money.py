from decimal import Decimal

import pytest

from app.domain.value_objects.money import Money


def test_create_from_string():
    money = Money.from_string("100.00")
    assert money.amount == Decimal("100.00")

def test_create_from_decimal():
    money = Money.from_decimal(Decimal("50.50"))
    assert money.amount == Decimal("50.50")

def test_apply_modifier():
    money = Money.from_string("100.00")
    result = money.apply_modifier(Decimal("0.95"))
    assert result.amount == Decimal("95.00")

def test_apply_modifier_rounds_correctly():
    money = Money.from_string("100.00")
    result = money.apply_modifier(Decimal("0.333"))
    assert result.amount == Decimal("33.30")

def test_negative_amount_raises_error():
    with pytest.raises(ValueError):
        Money(amount=Decimal("-10.00"))

def test_to_string():
    money = Money.from_string("99.90")
    assert money.to_string() == "99.90"

def test_str_representation():
    money = Money.from_string("123.45")
    assert str(money) == "123.45"

def test_multiplication():
    money = Money.from_string("100.00")
    result = money * Decimal("0.5")
    assert result.amount == Decimal("50.00")

def test_zero_amount():
    money = Money.from_string("0.00")
    assert money.amount == Decimal("0.00")

def test_immutability():
    money = Money.from_string("100.00")
    with pytest.raises(AttributeError):
        money.amount = Decimal("200.00")

def test_large_amount():
    money = Money.from_string("999999999.99")
    assert money.amount == Decimal("999999999.99")

def test_precision_maintained():
    money = Money.from_string("100.00")
    result = money.apply_modifier(Decimal("0.123456789"))
    assert result.amount == Decimal("12.35")

