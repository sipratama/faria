import { render, screen } from "@testing-library/react";

import { DashboardClient } from "./dashboard-client";
import type { DashboardData } from "@/lib/dashboard";

const emptyDashboard: DashboardData = {
  faria: {
    status: "healthy",
    modelAlias: "faria-household-main",
    dashboardApi: "healthy",
    database: "healthy",
    gateway: "not_monitored",
    router: "not_monitored",
    usageMonitoring: "not_connected",
  },
  personas: [
    { persona: "FINANCE", label: "Finance", activated: true, status: "IDLE", currentTask: null, lastActivityAt: null, lastErrorSummary: null },
    { persona: "GIVING", label: "Giving", activated: true, status: "WORKING", currentTask: "Giving record creation", lastActivityAt: null, lastErrorSummary: null },
    { persona: "HOME_OPS", label: "Home Ops", activated: false, status: "NOT_ACTIVATED", currentTask: null, lastActivityAt: null, lastErrorSummary: null },
    { persona: "PLANNER", label: "Planner", activated: false, status: "NOT_ACTIVATED", currentTask: null, lastActivityAt: null, lastErrorSummary: null },
  ],
  pendingConfirmations: [],
  householdSnapshot: {
    monthlyAllocation: { latestConfirmedPeriod: null, status: null, remainderIdr: null },
    savings: { activeGoalCount: 0, completedGoalCount: 0 },
    giving: { currentPeriod: "2099-01", currentPeriodCount: 0, latestType: null, latestPeriod: null, latestRecordedAt: null },
  },
  recentActivities: [],
  generatedAt: "2099-01-15T08:30:00Z",
};

test("renders health and distinguishes active from inactive personas", () => {
  render(<DashboardClient initialData={emptyDashboard} pollIntervalMs={0} />);

  expect(screen.getByText("Status FARIA")).toBeInTheDocument();
  expect(screen.getByText("Sehat")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Finance" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Giving" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Home Ops" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Planner" })).toBeInTheDocument();
  expect(screen.getAllByText("Belum diaktifkan")).toHaveLength(2);
  expect(screen.getByText("Giving record creation")).toBeInTheDocument();
});

test("renders honest empty states and no financial actions", () => {
  render(<DashboardClient initialData={emptyDashboard} pollIntervalMs={0} />);

  expect(screen.getByText("Belum ada aktivitas agen yang tercatat.")).toBeInTheDocument();
  expect(screen.getByText("Tidak ada draft alokasi yang menunggu konfirmasi.")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /konfirmasi alokasi/i })).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /buat target/i })).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: /perbarui/i })).toBeInTheDocument();
});

test("renders pending allocation and populated activity", () => {
  const populated: DashboardData = {
    ...emptyDashboard,
    pendingConfirmations: [{ type: "MONTHLY_ALLOCATION", referenceId: "draft-1", period: "2099-01", summary: "Monthly allocation 2099-01 waiting for confirmation.", createdAt: "2099-01-15T08:00:00Z" }],
    recentActivities: [{ activityId: "activity-1", persona: "GIVING", activityType: "GIVING_RECORDED", status: "SUCCEEDED", summary: "Sedekah giving recorded.", referenceType: null, referenceId: null, occurredAt: "2099-01-15T08:00:00Z" }],
  };

  render(<DashboardClient initialData={populated} pollIntervalMs={0} />);

  expect(screen.getByText("2099-01", { selector: ".period-stamp" })).toBeInTheDocument();
  expect(screen.getByText("Menunggu konfirmasi manusia.")).toBeInTheDocument();
  expect(screen.getByText("Sedekah giving recorded.")).toBeInTheDocument();
});

test("renders an explicit API outage state", () => {
  render(<DashboardClient initialData={null} initialError pollIntervalMs={0} />);

  expect(screen.getByRole("alert")).toHaveTextContent("FARIA belum dapat dihubungi.");
  expect(screen.getByRole("button", { name: "Coba lagi" })).toBeInTheDocument();
});
