import strawberry

from app.presentation.graphql.types import (
    PaymentInput,
    PaymentResult,
    PaymentError,
    SalesQueryInput,
    SalesReportType,
)
from app.presentation.graphql.resolvers import process_payment, get_sales_report


PaymentResponse = strawberry.union(
    "PaymentResponse",
    types=(PaymentResult, PaymentError),
)


@strawberry.type
class Query:
    """GraphQL Query type"""
    
    @strawberry.field
    async def sales(self, input: SalesQueryInput) -> SalesReportType:
        """Get sales report for a date range"""
        return await get_sales_report(input)
    
    @strawberry.field
    def health(self) -> str:
        """Health check endpoint"""
        return "OK"


@strawberry.type
class Mutation:
    """GraphQL Mutation type"""
    
    @strawberry.mutation
    async def payment(self, input: PaymentInput) -> PaymentResponse:
        """Process a payment"""
        return await process_payment(input)


schema = strawberry.Schema(query=Query, mutation=Mutation)

