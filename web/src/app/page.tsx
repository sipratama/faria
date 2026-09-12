import { DashboardClient } from "@/components/dashboard-client";
import { fetchDashboard } from "@/lib/dashboard";

export const dynamic = "force-dynamic";

export default async function Home() {
  let data = null;
  let initialError = false;
  try {
    data = await fetchDashboard();
  } catch {
    initialError = true;
  }
  return <DashboardClient initialData={data} initialError={initialError} />;
}
