from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from faria_household_mcp.dashboard import DashboardQueryService
from faria_household_mcp.dashboard_api import create_app
from faria_household_mcp.database import HouseholdDatabase


def test_api_exposes_exactly_three_read_only_get_routes(tmp_path) -> None:
    app = create_app(tmp_path / "faria.db")
    routes = {(route.path, frozenset(route.methods or set())) for route in app.routes}

    assert routes == {
        ("/health", frozenset({"GET"})),
        ("/api/dashboard", frozenset({"GET"})),
        ("/api/activities", frozenset({"GET"})),
    }
    client = TestClient(app)
    for path in ("/health", "/api/dashboard", "/api/activities"):
        for method in ("post", "put", "patch", "delete"):
            assert getattr(client, method)(path).status_code == 405


def test_health_and_empty_dashboard_responses_are_structured(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "faria.db"))

    health = client.get("/health")
    dashboard = client.get("/api/dashboard")
    activities = client.get("/api/activities")

    assert health.status_code == 200
    assert health.json()["status"] == "healthy"
    assert health.json()["database"] == "healthy"
    assert dashboard.status_code == 200
    assert dashboard.json()["faria"]["modelAlias"] == "faria-household-main"
    assert dashboard.json()["recentActivities"] == []
    assert activities.status_code == 200
    assert activities.json()["activities"] == []


def test_api_failure_is_generic_and_does_not_mutate_database(tmp_path) -> None:
    database = HouseholdDatabase(tmp_path / "faria.db")
    database.initialize()

    class FailingQuery(DashboardQueryService):
        def get_dashboard(self):
            raise RuntimeError(f"private path: {database.path}")

    client = TestClient(create_app(query_service=FailingQuery(database)))
    before = database.path.read_bytes()
    response = client.get("/api/dashboard")
    after = database.path.read_bytes()

    assert response.status_code == 503
    assert response.json() == {"detail": "Dashboard data is temporarily unavailable."}
    assert str(database.path) not in response.text
    assert before == after


def test_dashboard_clock_controls_current_period(tmp_path) -> None:
    database = HouseholdDatabase(tmp_path / "faria.db")
    query = DashboardQueryService(
        database,
        clock=lambda: datetime(2099, 7, 1, tzinfo=UTC),
    )
    client = TestClient(create_app(query_service=query))

    response = client.get("/api/dashboard")

    assert response.json()["householdSnapshot"]["giving"]["currentPeriod"] == "2099-07"
