from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class Money:
    """Value object representing monetary amounts with proper decimal handling"""
    
    amount: Decimal
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
    
    @classmethod
    def from_string(cls, value: str) -> "Money":
        """Create Money from a string representation"""
        return cls(amount=Decimal(value))
    
    @classmethod
    def from_decimal(cls, value: Decimal) -> "Money":
        """Create Money from a Decimal value"""
        return cls(amount=value)
    
    def apply_modifier(self, modifier: Decimal) -> "Money":
        """Apply a price modifier and return new Money instance"""
        new_amount = (self.amount * modifier).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return Money(amount=new_amount)
    
    def to_string(self) -> str:
        """Convert to string with 2 decimal places"""
        return str(self.amount.quantize(Decimal("0.01")))
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __mul__(self, other: Decimal) -> "Money":
        return self.apply_modifier(other)

