from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from strawberry.fastapi import GraphQLRouter

from app.infrastructure.config.settings import get_settings
from app.infrastructure.persistence.database import create_tables
from app.presentation.graphql.schema import schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    await create_tables()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )

    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")

    return app


app = create_app()


if __name__ == "__main__":    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
    )

