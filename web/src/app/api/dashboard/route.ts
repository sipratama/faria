import { NextResponse } from "next/server";

import { fetchDashboard } from "@/lib/dashboard";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return NextResponse.json(await fetchDashboard());
  } catch {
    return NextResponse.json(
      { error: "Status FARIA sementara tidak tersedia." },
      { status: 503 },
    );
  }
}
