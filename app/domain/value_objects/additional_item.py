from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re


class CourierService(str, Enum):
    """Supported courier services for cash on delivery"""
    
    YAMATO = "YAMATO"
    SAGAWA = "SAGAWA"


@dataclass(frozen=True)
class AdditionalItem:
    """Value object for payment-specific additional information"""
    
    last4: Optional[str] = None
    courier: Optional[CourierService] = None
    bank: Optional[str] = None
    account_number: Optional[str] = None
    cheque_number: Optional[str] = None
    
    def validate_last4(self) -> bool:
        """Validate that last4 is exactly 4 digits"""
        if self.last4 is None:
            return False
        return bool(re.match(r"^\d{4}$", self.last4))
    
    def validate_courier(self) -> bool:
        """Validate courier is a valid service"""
        return self.courier is not None
    
    def validate_bank_info(self) -> bool:
        """Validate bank transfer information"""
        return self.bank is not None and self.account_number is not None
    
    def validate_cheque_info(self) -> bool:
        """Validate cheque information"""
        return self.bank is not None and self.cheque_number is not None
    
    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "AdditionalItem":
        """Create AdditionalItem from a dictionary"""
        if data is None:
            return cls()
        
        courier = None
        if "courier" in data and data["courier"]:
            try:
                courier = CourierService(data["courier"])
            except ValueError:
                pass
        
        return cls(
            last4=data.get("last4"),
            courier=courier,
            bank=data.get("bank"),
            account_number=data.get("accountNumber") or data.get("account_number"),
            cheque_number=data.get("chequeNumber") or data.get("cheque_number"),
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        result = {}
        if self.last4:
            result["last4"] = self.last4
        if self.courier:
            result["courier"] = self.courier.value
        if self.bank:
            result["bank"] = self.bank
        if self.account_number:
            result["accountNumber"] = self.account_number
        if self.cheque_number:
            result["chequeNumber"] = self.cheque_number
        return result

