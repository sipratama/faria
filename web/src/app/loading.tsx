export default function Loading() {
  return (
    <main className="shell shell-loading" aria-busy="true" aria-live="polite">
      <p className="eyebrow">PRIVATE HOUSEHOLD SYSTEM / LOCAL ONLY</p>
      <h1>FARIA <em>Control Center</em></h1>
      <div className="loading-line" />
      <div className="loading-grid" aria-label="Memuat status FARIA">
        <span /><span /><span /><span />
      </div>
      <p>Memuat snapshot lokal...</p>
    </main>
  );
}
