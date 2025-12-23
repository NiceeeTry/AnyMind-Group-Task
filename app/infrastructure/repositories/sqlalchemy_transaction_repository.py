from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.transaction import Transaction
from app.domain.repositories.transaction_repository import TransactionRepository
from app.domain.value_objects.payment_method import PaymentMethod
from app.domain.value_objects.money import Money
from app.domain.value_objects.additional_item import AdditionalItem
from app.infrastructure.persistence.models import TransactionModel


class SqlAlchemyTransactionRepository(TransactionRepository):
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, transaction: Transaction) -> Transaction:
        """Save a transaction to the database"""
        model = self._to_model(transaction)
        self._session.add(model)
        await self._session.flush()
        return transaction


    async def get_hourly_sales(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> List[dict]:
        """Get aggregated hourly sales within a date range"""
        # Use date_trunc to group by hour
        hour_bucket = func.date_trunc('hour', TransactionModel.transaction_datetime)
        
        result = await self._session.execute(
            select(
                hour_bucket.label('hour'),
                func.sum(TransactionModel.final_price).label('total_sales'),
                func.sum(TransactionModel.points).label('total_points'),
            )
            .where(TransactionModel.transaction_datetime >= start_datetime)
            .where(TransactionModel.transaction_datetime <= end_datetime)
            .group_by(hour_bucket)
            .order_by(hour_bucket)
        )
        
        rows = result.all()
        return [
            {
                "datetime": row.hour,
                "sales": Decimal(str(row.total_sales)).quantize(Decimal("0.01")),
                "points": int(row.total_points),
            }
            for row in rows
        ]
    

    def _to_model(self, entity: Transaction) -> TransactionModel:
        """Convert domain entity to database model"""
        return TransactionModel(
            id=entity.id,
            customer_id=entity.customer_id,
            price=entity.price.amount,
            price_modifier=entity.price_modifier,
            payment_method=entity.payment_method.value,
            transaction_datetime=entity.transaction_datetime,
            final_price=entity.final_price.amount,
            points=entity.points,
            additional_item=entity.additional_item.to_dict() if entity.additional_item else None,
            created_at=entity.created_at,
        )


    def _to_entity(self, model: TransactionModel) -> Transaction:
        """Convert database model to domain entity"""
        return Transaction(
            id=model.id,
            customer_id=model.customer_id,
            price=Money.from_decimal(model.price),
            price_modifier=model.price_modifier,
            payment_method=PaymentMethod(model.payment_method),
            transaction_datetime=model.transaction_datetime,
            final_price=Money.from_decimal(model.final_price),
            points=model.points,
            additional_item=AdditionalItem.from_dict(model.additional_item),
            created_at=model.created_at,
        )

