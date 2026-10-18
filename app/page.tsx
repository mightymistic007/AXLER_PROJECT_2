'use client';

import { useState } from 'react';
import { MetricCard } from './components/MetricCard';
import { PipelineCanvas } from './components/PipelineCanvas';
import type { DashboardState } from './types';

const initialDashboard: DashboardState = {
  event: 'initial',
  running: true,
  circuit: 'closed',
  pipeline_status: 'connecting',
  metrics: { events_seen: 1240, accepted: 1228, quarantined: 12, quality_score: 99.0, error_rate: 0.96, throughput: 14.2, window_size: 100 },
  top_failures: [],
  incidents: [],
  snapshots: [],
  timestamp: new Date().toISOString(),
};

type Tab = 'overview' | 'incidents' | 'snapshots' | 'rules';

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [dashboard] = useState<DashboardState>(initialDashboard);

  const navItems: { id: Tab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'incidents', label: 'Incidents' },
    { id: 'snapshots', label: 'Snapshots' },
    { id: 'rules', label: 'Quality rules' },
  ];

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">IS</span>
          <div><strong>IceStream</strong><span>Lakehouse control plane</span></div>
        </div>
        <div className="top-actions">
          <span className="connection-pill is-live"><i />Live service</span>
        </div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <p className="nav-label">CONTROL PLANE</p>
          <nav aria-label="IceStream sections">
            {navItems.map((item) => (
              <button key={item.id} className={activeTab === item.id ? 'active' : ''} onClick={() => setActiveTab(item.id)}>
                <span className={`nav-icon icon-${item.id}`} />{item.label}
              </button>
            ))}
          </nav>
          <div className="sidebar-foot">
            <p>DEMO PROFILE</p>
            <strong>Local adapters</strong>
            <span>Kafka · Flink · Iceberg contract</span>
          </div>
        </aside>

        <section className="content">
          <div className="content-head">
            <div>
              <p className="eyebrow">REAL-TIME LAKEHOUSE OBSERVABILITY</p>
              <h1>Checkout telemetry</h1>
              <p>Governed streaming data from ingestion to the serving layer.</p>
            </div>
            <div className={`pipeline-chip status-${dashboard.pipeline_status}`}>
              <i />
              <span><b>{dashboard.pipeline_status}</b><small>Pipeline active</small></span>
            </div>
          </div>

          <div className="metric-grid">
            <MetricCard label="Events observed" value="1,240" detail="1,228 committed" history={[20, 45, 60, 80, 95]} />
            <MetricCard label="Quality score" value="99.0%" detail="100-event rolling window" tone="good" history={[95, 98, 99, 99, 99]} />
            <MetricCard label="Quarantined" value="12" detail="Rows protected from serving" tone="default" />
            <MetricCard label="Stream velocity" value="14.2/s" detail="Validated events per second" />
          </div>

          <div className="overview-grid">
            <article className="panel lineage-panel">
              <div className="panel-head">
                <div><p className="eyebrow">LIVE LINEAGE</p><h2>Pipeline topology</h2></div>
                <span className="stream-label">● STREAMING</span>
              </div>
              <PipelineCanvas circuitOpen={false} running={true} />
              <div className="lineage-legend">
                <span><i className="legend-good" />Healthy path</span>
                <span><i className="legend-watch" />Quality inspection</span>
                <span><i className="legend-bad" />Circuit blocked</span>
              </div>
            </article>

            <aside className="panel fault-panel">
              <div className="panel-head"><div><p className="eyebrow">CONTROLLED TEST</p><h2>Fault injection</h2></div></div>
              <p className="panel-copy">Introduce deterministic bad records and watch the quality gate isolate them.</p>
              <div className="fault-list">
                <button onClick={() => alert('Injecting null tax')} type="button"><span>NULL</span><div><strong>Null tax burst</strong><small>Break DQ-001</small></div><b>Inject</b></button>
                <button onClick={() => alert('Injecting schema drift')} type="button"><span>V2</span><div><strong>Schema drift</strong><small>Break DQ-003</small></div><b>Inject</b></button>
                <button onClick={() => alert('Injecting amount spike')} type="button"><span>₹↑</span><div><strong>Amount spike</strong><small>Break DQ-005</small></div><b>Inject</b></button>
              </div>
              <div className="breaker-box">
                <div><span className="breaker-light" /><p><small>CIRCUIT BREAKER</small><strong>closed</strong></p></div>
                <button type="button" onClick={() => alert('Resetting circuit breaker')}>Reset</button>
              </div>
            </aside>
          </div>
        </section>
      </div>
    </main>
  );
}
