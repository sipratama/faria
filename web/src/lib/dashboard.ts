export type FariaStatus = "healthy" | "working" | "attention";
export type PersonaStatus = "IDLE" | "WORKING" | "ERROR" | "NOT_ACTIVATED";

export interface AgentActivity {
  activityId: string;
  persona: "FINANCE" | "GIVING";
  activityType: string;
  status: "SUCCEEDED" | "FAILED";
  summary: string;
  referenceType: string | null;
  referenceId: string | null;
  occurredAt: string;
}

export interface DashboardPersona {
  persona: "FINANCE" | "GIVING" | "HOME_OPS" | "PLANNER";
  label: string;
  activated: boolean;
  status: PersonaStatus;
  currentTask: string | null;
  lastActivityAt: string | null;
  lastErrorSummary: string | null;
}

export interface DashboardData {
  faria: {
    status: FariaStatus;
    modelAlias: string;
    dashboardApi: "healthy";
    database: "healthy";
    gateway: "not_monitored";
    router: "not_monitored";
    usageMonitoring: "not_connected";
  };
  personas: DashboardPersona[];
  pendingConfirmations: Array<{
    type: "MONTHLY_ALLOCATION";
    referenceId: string;
    period: string;
    summary: string;
    createdAt: string;
  }>;
  householdSnapshot: {
    monthlyAllocation: {
      latestConfirmedPeriod: string | null;
      status: "CONFIRMED" | null;
      remainderIdr: number | null;
    };
    savings: {
      activeGoalCount: number;
      completedGoalCount: number;
    };
    giving: {
      currentPeriod: string;
      currentPeriodCount: number;
      latestType: "zakat_penghasilan" | "sedekah" | null;
      latestPeriod: string | null;
      latestRecordedAt: string | null;
    };
  };
  recentActivities: AgentActivity[];
  generatedAt: string;
}

const DASHBOARD_API_URL = process.env.FARIA_DASHBOARD_API_URL ?? "http://127.0.0.1:8000";

export async function fetchDashboard(): Promise<DashboardData> {
  const response = await fetch(`${DASHBOARD_API_URL}/api/dashboard`, {
    cache: "no-store",
    signal: AbortSignal.timeout(5_000),
  });
  if (!response.ok) {
    throw new Error("Dashboard API unavailable");
  }
  return (await response.json()) as DashboardData;
}
