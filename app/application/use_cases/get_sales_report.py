from typing import List

from app.domain.repositories.transaction_repository import TransactionRepository
from app.application.dto.payment_dto import SalesRequest, SalesResponse, HourlySales


class GetSalesReportUseCase:
    """Use case for getting hourly sales report"""
    
    def __init__(self, transaction_repository: TransactionRepository):
        self._transaction_repository = transaction_repository
    
    async def execute(self, request: SalesRequest) -> SalesResponse:
        """
        Get hourly sales report for a date range
        
        Args:
            request: Sales request DTO with date range
            
        Returns:
            Sales response with hourly breakdown
        """
        start_datetime = request.get_start_datetime()
        end_datetime = request.get_end_datetime()
        
        hourly_sales = await self._transaction_repository.get_hourly_sales(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        
        sales_list: List[HourlySales] = []
        for hour_data in hourly_sales:
            sales_list.append(HourlySales(
                datetime=hour_data["datetime"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                sales=str(hour_data["sales"]),
                points=int(hour_data["points"]),
            ))
        
        return SalesResponse(sales=sales_list)

