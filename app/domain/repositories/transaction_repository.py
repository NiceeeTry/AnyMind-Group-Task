from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from app.domain.entities.transaction import Transaction


class TransactionRepository(ABC):
    """Abstract repository interface for transaction persistence"""
    
    @abstractmethod
    async def save(self, transaction: Transaction) -> Transaction:
        """Save a transaction to the repository"""
        pass
    
    @abstractmethod
    async def get_hourly_sales(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> List[dict]:
        """Get aggregated hourly sales within a date range"""
        pass

