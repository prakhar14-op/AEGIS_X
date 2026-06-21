import React, { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import {
  Shield, Activity, Brain, Fingerprint, AlertTriangle, Zap, Radio,
  Wifi, WifiOff, ChevronDown, TrendingUp, Eye, Target, Cpu,
} from 'lucide-react'
import { useStore } from '../../services/store'
import { SimulatorScenario } from '../../services/api'
import Highcharts from 'highcharts'
import HighchartsMore from 'highcharts/highcharts-more'
import SolidGauge from 'highcharts/modules/solid-gauge'
import HighchartsReact from 'highcharts-react-official'

;(HighchartsMore as any)(Highcharts)
;(SolidGauge as any)(Highcharts)

const SCENARIOS: { key: SimulatorScenario; label: string; color: string; desc: string }[] = [
  { key: 'normal', label: 'Normal User', color: '#10B981', desc: 'Calm browsing' },
  { key: 'scam', label: 'Scam Victim', color: '#F59E0B', desc: 'Coercion attack' },
  { key: 'malware', label: 'Malware Bot', color: '#EF4444', desc: 'Remote access' },
]

function getTrustColor(score: number) {
  if (score > 85) return '#10B981'
  if (score > 60) return '#F59E0B'
  if (score > 40) return '#F97316'
  return '#EF4444'
}

function getTrustType(score: number): 'success' | 'warning' | 'error' {
  if (score > 85) return 'success'
  if (score > 60) return 'warning'
  return 'error'
}

const StatCard: React.FC<{ label: string; value: string; sub: string; color: string; icon: React.ReactNode }> = ({ label, value, sub, color, icon }) => (
  <motion.div
    initial={{ opacity: 0, y: 16 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ y: -3, boxShadow: '0 12px 40px rgba(0,0,0,0.20)' }}
    transition={{ duration: 0.3 }}
    style={{ background: 'var(--bg-card)', borderRadius: 16, padding: '20px 22px', border: '1px solid var(--border-light)', boxShadow: '0 2px 12px rgba(0,0,0,0.08)' }}
  >
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
      <div>
        <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.18em', color: 'var(--text-muted)', margin: '0 0 8px', fontFamily: 'JetBrains Mono, monospace' }}>{label}</p>
        <p style={{ fontSize: 28, fontWeight: 900, color: 'var(--text-main)', margin: '0 0 4px', lineHeight: 1, fontFamily: 'Space Grotesk, sans-serif' }}>{value}</p>
        <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: 0 }}>{sub}</p>
      </div>
      <div style={{ width: 42, height: 42, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', background: `${color}15`, border: `1px solid ${color}30` }}>
        {icon}
      </div>
    </div>
    <div style={{ marginTop: 14, height: 3, background: 'rgba(255,255,255,0.05)', borderRadius: 99, overflow: 'hidden' }}>
      <div style={{ height: '100%', width: '70%', background: `linear-gradient(to right, ${color}, ${color}80)`, borderRadius: 99 }} />
    </div>
  </motion.div>
)

const Section: React.FC<{ title: string; accent: string; count?: number; defaultOpen?: boolean; liveIndicator?: boolean; children: React.ReactNode }> = ({ title, accent, count, defaultOpen = true, liveIndicator, children }) => {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div style={{ margin: '0 0 12px', borderRadius: 16, overflow: 'hidden' }}>
      <div onClick={() => setOpen(o => !o)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '13px 20px', cursor: 'pointer', userSelect: 'none', background: open ? `${accent}08` : `${accent}05`, border: open ? `1px solid ${accent}25` : `1px solid ${accent}12`, borderRadius: open ? '16px 16px 0 0' : 16, position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 14, fontWeight: 700, color: accent, letterSpacing: '0.02em', fontFamily: 'Space Grotesk, sans-serif' }}>{title}</span>
          {count !== undefined && count > 0 && (
            <span style={{ background: accent, color: '#fff', fontSize: 10, fontWeight: 800, padding: '2px 8px', borderRadius: 999 }}>{count}</span>
          )}
          {liveIndicator && (
            <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, color: accent }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: accent, display: 'inline-block', animation: 'pulse 1.5s ease-in-out infinite' }} />
              LIVE
            </span>
          )}
        </div>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }} style={{ width: 28, height: 28, background: `${accent}15`, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: accent }}>
          <ChevronDown size={14} />
        </motion.div>
      </div>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div key="body" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }} style={{ overflow: 'hidden', border: `1px solid ${accent}18`, borderTop: 'none', borderRadius: '0 0 16px 16px', background: 'var(--bg-card)' }}>
            <div style={{ padding: '16px 20px' }}>{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

const LiveMonitor: React.FC = () => {
  const { state, connect, switchScenario } = useStore()
  const { trustScore, effectiveTrust, decision, cognitiveState, similarity, driftDetected, driftSeverity, eventCount, velocity, acceleration, isConnected, scenario, latencyMs, confidence, entropy, trend, anomalyScore, fraudProbability, fraudTrajectory, intentVector, timeline } = state
  const chartRef = useRef<HighchartsReact.RefObject>(null)

  useEffect(() => { if (!isConnected) connect('normal') }, [])

  const trustColor = getTrustColor(trustScore)
  const cogColors: Record<string, string> = { calm: '#10B981', focused: '#3B82F6', distressed: '#F59E0B', panicked: '#F97316', coerced: '#EF4444', robotic: '#8B5CF6' }
  const cogColor = cogColors[cognitiveState] || '#94A3B8'

  const gaugeOptions: Highcharts.Options = {
    chart: { type: 'solidgauge', height: 220, backgroundColor: 'transparent', margin: [0, 0, 0, 0] },
    title: undefined,
    pane: { startAngle: -130, endAngle: 130, background: [{ backgroundColor: 'rgba(255,255,255,0.03)', borderWidth: 0, innerRadius: '80%', outerRadius: '100%', shape: 'arc' }] },
    yAxis: { min: 0, max: 100, lineWidth: 0, tickWidth: 0, labels: { enabled: false }, stops: [[0.3, '#EF4444'], [0.6, '#F59E0B'], [0.85, '#10B981']] as any },
    series: [{ type: 'solidgauge', name: 'Trust', data: [Math.round(trustScore)], dataLabels: { enabled: true, format: '<div style="text-align:center"><span style="font-size:42px;font-weight:800;color:' + trustColor + ';font-family:Space Grotesk">{y}</span><br/><span style="font-size:11px;color:#64748B;font-family:JetBrains Mono">TRUST SCORE</span></div>', borderWidth: 0, y: -20 }, rounded: true }],
    tooltip: { enabled: false },
    credits: { enabled: false },
    plotOptions: { solidgauge: { innerRadius: '80%', dataLabels: { y: -30, borderWidth: 0, useHTML: true } } },
  }

  const miniChartOptions: Highcharts.Options = {
    chart: { type: 'areaspline', height: 80, backgroundColor: 'transparent', margin: [5, 0, 5, 0], spacing: [0, 0, 0, 0] },
    title: undefined,
    xAxis: { visible: false },
    yAxis: { visible: false, min: 0, max: 100 },
    legend: { enabled: false },
    tooltip: { enabled: false },
    credits: { enabled: false },
    plotOptions: { areaspline: { fillColor: { linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 }, stops: [[0, trustColor + '40'], [1, trustColor + '00']] }, lineWidth: 2, lineColor: trustColor, marker: { enabled: false }, threshold: null } },
    series: [{ type: 'areaspline', data: timeline.slice(-20).map(t => t.trust) }],
  }

  return (
    <div>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 20px', borderRadius: 14, marginBottom: 20, background: isConnected ? 'rgba(16,185,129,0.05)' : 'rgba(239,68,68,0.05)', border: `1px solid ${isConnected ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)'}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {isConnected ? <Wifi size={16} style={{ color: '#10B981' }} /> : <WifiOff size={16} style={{ color: '#EF4444' }} />}
          <span style={{ fontSize: 12, fontWeight: 600, color: isConnected ? '#10B981' : '#EF4444', fontFamily: 'JetBrains Mono, monospace' }}>
            {isConnected ? 'Pipeline online · WebSocket connected · Streaming every 2s' : 'Pipeline offline — connect to start monitoring'}
          </span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {SCENARIOS.map(s => (
            <button key={s.key} onClick={() => switchScenario(s.key)} style={{ padding: '6px 14px', borderRadius: 999, fontSize: 11, fontWeight: 700, cursor: 'pointer', background: scenario === s.key ? `${s.color}18` : 'transparent', border: `1px solid ${scenario === s.key ? s.color : 'var(--border-light)'}`, color: scenario === s.key ? s.color : 'var(--text-muted)', transition: 'all 0.15s' }}>
              {s.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 20 }}>
        <StatCard label="Similarity" value={similarity.toFixed(3)} sub="Cosine vs baseline" color={similarity > 0.85 ? '#10B981' : similarity > 0.6 ? '#F59E0B' : '#EF4444'} icon={<Fingerprint size={20} style={{ color: similarity > 0.85 ? '#10B981' : '#F59E0B' }} />} />
        <StatCard label="Drift Status" value={driftDetected ? driftSeverity.toUpperCase() : 'NONE'} sub={`CUSUM detector`} color={driftDetected ? '#EF4444' : '#10B981'} icon={<AlertTriangle size={20} style={{ color: driftDetected ? '#EF4444' : '#10B981' }} />} />
        <StatCard label="Events Processed" value={String(eventCount)} sub={`Latency: ${latencyMs.toFixed(0)}ms`} color="#3B82F6" icon={<Activity size={20} style={{ color: '#3B82F6' }} />} />
        <StatCard label="Fraud Probability" value={`${(fraudProbability * 100).toFixed(1)}%`} sub={`Trajectory: ${fraudTrajectory}`} color={fraudProbability > 0.5 ? '#EF4444' : '#10B981'} icon={<Target size={20} style={{ color: fraudProbability > 0.5 ? '#EF4444' : '#10B981' }} />} />
      </div>

      {/* Main Panel: Gauge + Chart + Decision */}
      <Section title="Trust Engine" accent="#10B981" defaultOpen={true} liveIndicator={isConnected}>
        <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr 240px', gap: 20, alignItems: 'start' }}>
          {/* Gauge */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <HighchartsReact highcharts={Highcharts} options={gaugeOptions} ref={chartRef} />
            <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>VELOCITY</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: velocity < -0.01 ? '#EF4444' : '#10B981', fontFamily: 'Space Grotesk, sans-serif' }}>{velocity > 0 ? '+' : ''}{velocity.toFixed(4)}</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>TREND</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: trend === 'declining' ? '#EF4444' : '#10B981', fontFamily: 'Space Grotesk, sans-serif' }}>{trend.toUpperCase()}</div>
              </div>
            </div>
          </div>

          {/* Mini trust timeline */}
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8, fontFamily: 'JetBrains Mono, monospace' }}>TRUST TIMELINE (last 20 events)</div>
            <HighchartsReact highcharts={Highcharts} options={miniChartOptions} />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, marginTop: 12 }}>
              <div style={{ padding: '8px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-light)' }}>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>ENTROPY</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#8B5CF6', fontFamily: 'Space Grotesk, sans-serif' }}>{entropy.toFixed(3)}</div>
              </div>
              <div style={{ padding: '8px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-light)' }}>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>ACCEL</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#3B82F6', fontFamily: 'Space Grotesk, sans-serif' }}>{acceleration.toFixed(4)}</div>
              </div>
              <div style={{ padding: '8px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-light)' }}>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace' }}>CONFIDENCE</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#F59E0B', fontFamily: 'Space Grotesk, sans-serif' }}>{(confidence * 100).toFixed(0)}%</div>
              </div>
            </div>
          </div>

          {/* Decision + Cognitive */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ padding: 16, borderRadius: 12, background: decision === 'ALLOW' ? 'rgba(16,185,129,0.06)' : decision === 'STEP_UP' ? 'rgba(245,158,11,0.06)' : 'rgba(239,68,68,0.06)', border: `1px solid ${decision === 'ALLOW' ? 'rgba(16,185,129,0.2)' : decision === 'STEP_UP' ? 'rgba(245,158,11,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
              <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.18em', color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'JetBrains Mono, monospace' }}>DECISION</div>
              <AnimatePresence mode="wait">
                <motion.div key={decision} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} style={{ fontSize: 24, fontWeight: 900, color: decision === 'ALLOW' ? '#10B981' : decision === 'STEP_UP' ? '#F59E0B' : '#EF4444', fontFamily: 'Space Grotesk, sans-serif' }}>
                  {decision === 'STEP_UP' ? 'STEP-UP' : decision}
                </motion.div>
              </AnimatePresence>
            </div>
            <div style={{ padding: 16, borderRadius: 12, background: `${cogColor}08`, border: `1px solid ${cogColor}20` }}>
              <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.18em', color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'JetBrains Mono, monospace' }}>COGNITIVE STATE</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Brain size={18} color={cogColor} />
                <span style={{ fontSize: 18, fontWeight: 800, color: cogColor, fontFamily: 'Space Grotesk, sans-serif' }}>{cognitiveState.toUpperCase()}</span>
              </div>
            </div>
            <div style={{ padding: 16, borderRadius: 12, background: 'rgba(139,92,246,0.04)', border: '1px solid rgba(139,92,246,0.12)' }}>
              <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.18em', color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'JetBrains Mono, monospace' }}>ANOMALY</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: anomalyScore > 0.3 ? '#EF4444' : '#10B981', fontFamily: 'Space Grotesk, sans-serif' }}>{(anomalyScore * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>
      </Section>

      {/* Intent Vector */}
      <Section title="Fraud Intent Vector" accent="#EF4444" defaultOpen={fraudProbability > 0.2} count={fraudProbability > 0.5 ? 1 : 0}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
          {[
            { label: 'Coercion', value: intentVector.coercion_probability, color: '#EF4444' },
            { label: 'Takeover', value: intentVector.takeover_probability, color: '#F97316' },
            { label: 'Anomaly', value: intentVector.anomaly_severity, color: '#F59E0B' },
            { label: 'Robotic', value: intentVector.robotic_probability, color: '#8B5CF6' },
          ].map(item => (
            <div key={item.label} style={{ padding: '14px 16px', borderRadius: 12, background: `${item.color}06`, border: `1px solid ${item.color}15` }}>
              <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: 6, fontFamily: 'JetBrains Mono, monospace' }}>{item.label}</div>
              <div style={{ fontSize: 22, fontWeight: 800, color: item.value > 0.5 ? item.color : 'var(--text-sub)', fontFamily: 'Space Grotesk, sans-serif' }}>{(item.value * 100).toFixed(0)}%</div>
              <div style={{ height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 99, overflow: 'hidden', marginTop: 8 }}>
                <motion.div animate={{ width: `${item.value * 100}%` }} transition={{ duration: 0.6 }} style={{ height: '100%', background: item.color, borderRadius: 99 }} />
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Alert Banner */}
      <AnimatePresence>
        {(cognitiveState === 'panicked' || cognitiveState === 'coerced' || cognitiveState === 'robotic') && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} style={{ background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: 14, padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 12, marginTop: 12 }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: 'rgba(239,68,68,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <AlertTriangle size={20} color="#EF4444" />
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#EF4444', fontFamily: 'Space Grotesk, sans-serif' }}>
                {cognitiveState === 'robotic' ? 'AUTOMATED BEHAVIOR DETECTED' : cognitiveState === 'coerced' ? 'COERCION DETECTED — USER UNDER DURESS' : 'COGNITIVE DISTRESS — POTENTIAL SOCIAL ENGINEERING'}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-sub)', marginTop: 3, fontFamily: 'JetBrains Mono, monospace' }}>
                {state.reasons.length > 0 ? state.reasons[0] : 'Behavioral anomaly detected — monitoring escalated.'}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}`}</style>
    </div>
  )
}

export default LiveMonitor
