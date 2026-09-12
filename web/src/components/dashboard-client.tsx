"use client";

import { useCallback, useEffect, useState } from "react";

import type { DashboardData, DashboardPersona, FariaStatus } from "@/lib/dashboard";

const statusLabels: Record<FariaStatus, string> = {
  healthy: "Sehat",
  working: "Sedang bekerja",
  attention: "Perlu perhatian",
};

const personaLabels = {
  IDLE: "Siaga",
  WORKING: "Bekerja",
  ERROR: "Perlu perhatian",
  NOT_ACTIVATED: "Belum diaktifkan",
} as const;

const idr = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  maximumFractionDigits: 0,
});

function PersonaCard({ persona, index }: { persona: DashboardPersona; index: number }) {
  return (
    <article
      className={`persona-card status-${persona.status.toLowerCase()}`}
      style={{ "--delay": `${index * 70}ms` } as React.CSSProperties}
    >
      <div className="persona-topline">
        <span className="persona-number">0{index + 1}</span>
        <span className="signal" aria-hidden="true" />
      </div>
      <h3>{persona.label}</h3>
      <p className="persona-status">{personaLabels[persona.status]}</p>
      <p className="persona-detail">
        {!persona.activated
          ? "Kapabilitas direncanakan untuk fase berikutnya."
          : persona.currentTask ?? persona.lastErrorSummary ?? "Tidak ada tugas aktif."}
      </p>
    </article>
  );
}

function EmptyState({ children }: { children: React.ReactNode }) {
  return <p className="empty-state">{children}</p>;
}

export function DashboardClient({
  initialData,
  initialError = false,
  pollIntervalMs = 10_000,
}: {
  initialData: DashboardData | null;
  initialError?: boolean;
  pollIntervalMs?: number;
}) {
  const [data, setData] = useState(initialData);
  const [hasError, setHasError] = useState(initialError);
  const [refreshing, setRefreshing] = useState(false);

  const refresh = useCallback(async () => {
    setRefreshing(true);
    try {
      const response = await fetch("/api/dashboard", { cache: "no-store" });
      if (!response.ok) throw new Error("Dashboard unavailable");
      setData((await response.json()) as DashboardData);
      setHasError(false);
    } catch {
      setHasError(true);
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (pollIntervalMs <= 0) return;
    const interval = window.setInterval(refresh, pollIntervalMs);
    return () => window.clearInterval(interval);
  }, [pollIntervalMs, refresh]);

  if (!data) {
    return (
      <main className="shell shell-error">
        <section className="fatal-state" role="alert">
          <span className="fatal-mark">F</span>
          <p className="eyebrow">LOCAL CONTROL CENTER</p>
          <h1>FARIA belum dapat dihubungi.</h1>
          <p>
            Dashboard API atau database lokal tidak tersedia. Data rumah tangga tidak diubah.
          </p>
          <button type="button" onClick={refresh} disabled={refreshing}>
            {refreshing ? "Menghubungkan..." : "Coba lagi"}
          </button>
        </section>
      </main>
    );
  }

  const allocation = data.householdSnapshot.monthlyAllocation;
  const savings = data.householdSnapshot.savings;
  const giving = data.householdSnapshot.giving;

  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">PRIVATE HOUSEHOLD SYSTEM / LOCAL ONLY</p>
          <h1>FARIA <em>Control Center</em></h1>
          <p className="hero-note">Satu rumah tangga. Satu runtime. Empat pandangan kerja.</p>
        </div>
        <div className={`overall-status status-${data.faria.status}`}>
          <span className="signal" aria-hidden="true" />
          <div>
            <span>Status FARIA</span>
            <strong>{statusLabels[data.faria.status]}</strong>
          </div>
        </div>
      </header>

      {hasError && (
        <div className="warning-banner" role="alert">
          Pembaruan terakhir gagal. Menampilkan snapshot lokal terakhir yang tersedia.
        </div>
      )}

      <section className="system-strip" aria-label="Status sistem">
        <div><span>Model alias</span><strong>{data.faria.modelAlias}</strong></div>
        <div><span>Dashboard API</span><strong className="good">Terpantau sehat</strong></div>
        <div><span>SQLite</span><strong className="good">Terpantau sehat</strong></div>
        <div><span>Gateway / 9Router</span><strong>Belum dipantau</strong></div>
        <div><span>Penggunaan AI</span><strong>Belum terhubung</strong></div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <p className="eyebrow">LOGICAL PERSONAS</p>
            <h2>Siapa yang sedang bergerak?</h2>
          </div>
          <button className="refresh-button" type="button" onClick={refresh} disabled={refreshing}>
            <span aria-hidden="true">↻</span> {refreshing ? "Memperbarui" : "Perbarui"}
          </button>
        </div>
        <div className="persona-grid">
          {data.personas.map((persona, index) => (
            <PersonaCard key={persona.persona} persona={persona} index={index} />
          ))}
        </div>
      </section>

      <div className="content-grid">
        <section className="panel pending-panel">
          <div className="panel-heading">
            <p className="eyebrow">HUMAN-IN-THE-LOOP</p>
            <span className="count">{data.pendingConfirmations.length}</span>
          </div>
          <h2>Menunggu Konfirmasi</h2>
          {data.pendingConfirmations.length === 0 ? (
            <EmptyState>Tidak ada draft alokasi yang menunggu konfirmasi.</EmptyState>
          ) : (
            <ul className="pending-list">
              {data.pendingConfirmations.map((item) => (
                <li key={item.referenceId}>
                  <span className="period-stamp">{item.period}</span>
                  <div><strong>Alokasi bulanan</strong><p>Menunggu konfirmasi manusia.</p></div>
                </li>
              ))}
            </ul>
          )}
          <p className="boundary-note">Tindakan finansial tetap dilakukan melalui Telegram.</p>
        </section>

        <section className="panel activity-panel">
          <div className="panel-heading">
            <p className="eyebrow">APPEND-ONLY LOG</p>
            <span className="count">{data.recentActivities.length}</span>
          </div>
          <h2>Aktivitas Terbaru</h2>
          {data.recentActivities.length === 0 ? (
            <EmptyState>Belum ada aktivitas agen yang tercatat.</EmptyState>
          ) : (
            <ol className="activity-list">
              {data.recentActivities.map((activity) => (
                <li key={activity.activityId}>
                  <span className={`activity-dot ${activity.status.toLowerCase()}`} />
                  <div>
                    <span>{activity.persona === "FINANCE" ? "Finance" : "Giving"}</span>
                    <strong>{activity.summary}</strong>
                  </div>
                  <time dateTime={activity.occurredAt}>{formatTimestamp(activity.occurredAt)}</time>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>

      <section className="snapshot-section">
        <div className="section-heading">
          <div><p className="eyebrow">READ-ONLY SNAPSHOT</p><h2>Ringkasan Rumah Tangga</h2></div>
          <p className="generated">Diperbarui {formatTimestamp(data.generatedAt)}</p>
        </div>
        <div className="snapshot-grid">
          <article>
            <span>Alokasi bulanan</span>
            <strong>{allocation.latestConfirmedPeriod ?? "Belum ada"}</strong>
            <p>
              {allocation.remainderIdr === null
                ? "Belum ada alokasi terkonfirmasi."
                : `Sisa belum dialokasikan ${idr.format(allocation.remainderIdr)}`}
            </p>
          </article>
          <article>
            <span>Target tabungan</span>
            <strong>{savings.activeGoalCount} aktif</strong>
            <p>{savings.completedGoalCount} target selesai.</p>
          </article>
          <article>
            <span>Giving / {giving.currentPeriod}</span>
            <strong>{giving.currentPeriodCount} catatan</strong>
            <p>{giving.latestType ? `Terakhir: ${giving.latestType.replace("_", " ")}` : "Belum ada catatan giving."}</p>
          </article>
        </div>
      </section>

      <footer>
        <span>FARIA / RF-05</span>
        <span>Monitoring lokal · tanpa kontrol finansial</span>
      </footer>
    </main>
  );
}

function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat("id-ID", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Jakarta",
  }).format(new Date(value));
}
