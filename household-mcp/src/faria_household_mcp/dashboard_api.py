from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from faria_household_mcp.dashboard import (
    ActivitiesResponse,
    DashboardQueryService,
    DashboardSnapshot,
)
from faria_household_mcp.database import HouseholdDatabase, utc_now


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel, populate_by_name=True)

    status: str
    database: str
    timestamp: str


def create_app(
    database_path: str | Path | None = None,
    query_service: DashboardQueryService | None = None,
) -> FastAPI:
    service = query_service or DashboardQueryService(HouseholdDatabase(database_path))
    app = FastAPI(
        title="FARIA Dashboard API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        try:
            service.health()
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail="Dashboard data is temporarily unavailable.",
            ) from error
        return HealthResponse(status="healthy", database="healthy", timestamp=utc_now())

    @app.get("/api/dashboard", response_model=DashboardSnapshot)
    def dashboard() -> DashboardSnapshot:
        try:
            return service.get_dashboard()
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail="Dashboard data is temporarily unavailable.",
            ) from error

    @app.get("/api/activities", response_model=ActivitiesResponse)
    def activities() -> ActivitiesResponse:
        try:
            return service.get_activities()
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail="Dashboard data is temporarily unavailable.",
            ) from error

    return app


app = create_app()


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
