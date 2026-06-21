import React, { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import {
  Shield, Activity, Brain, Fingerprint, AlertTriangle, Zap, Radio,
  Wifi, WifiOff, TrendingUp, Target, ChevronDown,
} from 'lucide-react'
import { useStore } from '../../services/store'
import { SimulatorScenario } from '../../services/api'
import Highcharts from 'highcharts'
import HighchartsMore from 'highcharts/highcharts-more'
import HighchartsReact from 'highcharts-react-official'
import Stepper, { Step } from '../components/Stepper'

;(HighchartsMore as any)(Highcharts)

const SCENARIOS: { key: SimulatorScenario; label: string; color: string }[] = [
  { key: 'normal', label: 'Normal User', color: '#10B981' },
  { key: 'scam', label: 'Scam Victim', color: '#F59E0B' },
  { key: 'malware', label: 'Malware Bot', color: '#EF4444' },
]

function getTrustColor(score: number) {
  if (score > 85) return '#10B981'
  if (score > 60) return '#F59E0B'
  if (score > 40) return '#F97316'
  return '#EF4444'
}

const StatCard: React.FC<{ label: string; value: string; sub: string; color: string; icon: React.ReactNode }> = ({ label, value, sub, color, icon }) => (
  <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} whileHover={{ y: -3 }} transition={{ duration: 0.3 }}
    style={{ background: 'var(--bg-card)', borderRadius: 16, padding: '18px 20px', border: '1px solid var(--border-light)' }}>
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
      <div>
        <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.15em', color: 'var(--text-muted)', margin: '0 0 6px', fontFamily: 'JetBrains Mono' }}>{label}</p>
        <p style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-main)', margin: '0 0 3px', lineHeight: 1, fontFamily: 'Space Grotesk' }}>{value}</p>
        <p style={{ fontSize: 10, color: 'var(--text-muted)', margin: 0 }}>{sub}</p>
      </div>
      <div style={{ width: 38, height: 38, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', background: `${color}12`, border: `1px solid ${color}25` }}>
        {icon}
      </div>
    </div>
  </motion.div>
)

const LiveMonitor: React.FC = () => {
  const { state, connect, switchScenario } = useStore()
  const { trustScore, decision, cognitiveState, similarity, driftDetected, driftSeverity, eventCount, velocity, acceleration, isConnected, scenario, latencyMs, confidence, entropy, trend, anomalyScore, fraudProbability, fraudTrajectory, intentVector, timeline } = state

  useEffect(() => { if (!isConnected) connect('normal') }, [])

  const trustColor = getTrustColor(trustScore)
  const cogColors: Record<string, string> = { calm: '#10B981', focused: '#3B82F6', distressed: '#F59E0B', panicked: '#F97316', coerced: '#EF4444', robotic: '#8B5CF6' }
  const cogColor = cogColors[cognitiveState] || '#94A3B8'

  const gaugeOptions: Highcharts.Options = {
    chart: { type: 'gauge', backgroundColor: 'transparent', height: 200, margin: [0, 0, 0, 0] },
    title: undefined,
    pane: { startAngle: -90, endAngle: 90, background: undefined },
    yAxis: {
      min: 0, max: 100, lineWidth: 0, tickWidth: 0, labels: { enabled: false },
      plotBands: [
        { from: 0, to: 40, color: 'rgba(239,68,68,0.15)', innerRadius: '85%', outerRadius: '100%' },
        { from: 40, to: 70, color: 'rgba(245,158,11,0.15)', innerRadius: '85%', outerRadius: '100%' },
        { from: 70, to: 100, color: 'rgba(16,185,129,0.15)', innerRadius: '85%', outerRadius: '100%' },
      ],
    },
    series: [{
      type: 'gauge' as any,
      data: [Math.round(trustScore)],
      dial: { radius: '75%', backgroundColor: trustColor, baseWidth: 8, topWidth: 1, baseLength: '0%', rearLength: '0%' },
      pivot: { backgroundColor: trustColor, radius: 6, borderWidth: 0 },
      dataLabels: { enabled: true, format: `<div style="text-align:center"><span style="font-size:36px;font-weight:800;color:${trustColor};font-family:Space Grotesk">{y}</span><br/><span style="font-size:10px;color:#64748B;font-family:JetBrains Mono">TRUST SCORE</span></div>`, borderWidth: 0, y: 30, useHTML: true },
    }],
    tooltip: { enabled: false },
    credits: { enabled: false },
  }

  const splineOptions: Highcharts.Options = {
    chart: { type: 'areaspline', backgroundColor: 'transparent', height: 160, margin: [10, 10, 30, 30] },
    title: undefined,
    xAxis: { visible: false },
    yAxis: { visible: false, min: 0, max: 100 },
    legend: { enabled: false },
    credits: { enabled: false },
    tooltip: { enabled: false },
    plotOptions: { areaspline: { fillColor: { linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 }, stops: [[0, `${trustColor}30`], [1, `${trustColor}00`]] as any }, lineWidth: 2.5, color: trustColor, marker: { enabled: false }, animation: { duration: 800 } } },
    series: [{ type: 'areaspline', data: timeline.slice(-25).map(t => t.trust), name: 'Trust' }],
  }

  return (
    <div>
      {/* Header banner */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 18px', borderRadius: 12, marginBottom: 18, background: isConnected ? 'rgba(16,185,129,0.04)' : 'rgba(239,68,68,0.04)', border: `1px solid ${isConnected ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)'}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {isConnected ? <Wifi size={14} color="#10B981" /> : <WifiOff size={14} color="#EF4444" />}
          <span style={{ fontSize: 11, fontWeight: 600, color: isConnected ? '#10B981' : '#EF4444', fontFamily: 'JetBrains Mono' }}>
            {isConnected ? 'Pipeline active · streaming every 2s' : 'Disconnected'}
          </span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {SCENARIOS.map(s => (
            <button key={s.key} onClick={() => switchScenario(s.key)} style={{ padding: '5px 12px', borderRadius: 999, fontSize: 10, fontWeight: 700, cursor: 'pointer', background: scenario === s.key ? `${s.color}15` : 'transparent', border: `1px solid ${scenario === s.key ? s.color : 'var(--border-light)'}`, color: scenario === s.key ? s.color : 'var(--text-muted)', transition: 'all 0.15s' }}>
              {s.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 18 }}>
        <StatCard label="Similarity" value={similarity.toFixed(3)} sub="Cosine vs baseline" color={similarity > 0.85 ? '#10B981' : '#F59E0B'} icon={<Fingerprint size={18} style={{ color: similarity > 0.85 ? '#10B981' : '#F59E0B' }} />} />
        <StatCard label="Drift" value={driftDetected ? driftSeverity.toUpperCase() : 'NONE'} sub="CUSUM detector" color={driftDetected ? '#EF4444' : '#10B981'} icon={<AlertTriangle size={18} style={{ color: driftDetected ? '#EF4444' : '#10B981' }} />} />
        <StatCard label="Events" value={String(eventCount)} sub={`${latencyMs.toFixed(0)}ms latency`} color="#3B82F6" icon={<Activity size={18} style={{ color: '#3B82F6' }} />} />
        <StatCard label="Fraud Risk" value={`${(fraudProbability * 100).toFixed(0)}%`} sub={fraudTrajectory} color={fraudProbability > 0.5 ? '#EF4444' : '#10B981'} icon={<Target size={18} style={{ color: fraudProbability > 0.5 ? '#EF4444' : '#10B981' }} />} />
      </div>

      {/* Main Grid: Gauge | Spline Chart + Metrics | Decision Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr 260px', gap: 16, marginBottom: 18 }}>
        {/* Gauge */}
        <div style={{ background: 'var(--bg-card)', borderRadius: 14, padding: '16px 12px', border: '1px solid var(--border-light)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <HighchartsReact highcharts={Highcharts} options={gaugeOptions} />
          <div style={{ display: 'flex', gap: 20, marginTop: 4 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>VELOCITY</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: velocity < -0.01 ? '#EF4444' : '#10B981', fontFamily: 'Space Grotesk' }}>{velocity > 0 ? '+' : ''}{velocity.toFixed(4)}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>TREND</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: trend === 'declining' ? '#EF4444' : '#10B981', fontFamily: 'Space Grotesk' }}>{trend.toUpperCase()}</div>
            </div>
          </div>
        </div>

        {/* Spline Chart + Temporal Metrics */}
        <div style={{ background: 'var(--bg-card)', borderRadius: 14, padding: 16, border: '1px solid var(--border-light)' }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.12em' }}>Trust Timeline</div>
          <HighchartsReact highcharts={Highcharts} options={splineOptions} />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginTop: 10 }}>
            {[
              { label: 'ENTROPY', value: entropy.toFixed(3), color: '#8B5CF6' },
              { label: 'ACCEL', value: acceleration.toFixed(4), color: '#3B82F6' },
              { label: 'CONFIDENCE', value: `${(confidence * 100).toFixed(0)}%`, color: '#F59E0B' },
            ].map(m => (
              <div key={m.label} style={{ padding: '6px 10px', borderRadius: 8, background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-light)' }}>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>{m.label}</div>
                <div style={{ fontSize: 15, fontWeight: 700, color: m.color, fontFamily: 'Space Grotesk' }}>{m.value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Decision + Cognitive */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ padding: 14, borderRadius: 12, background: decision === 'ALLOW' ? 'rgba(16,185,129,0.05)' : decision === 'STEP_UP' ? 'rgba(245,158,11,0.05)' : 'rgba(239,68,68,0.05)', border: `1px solid ${decision === 'ALLOW' ? 'rgba(16,185,129,0.15)' : decision === 'STEP_UP' ? 'rgba(245,158,11,0.15)' : 'rgba(239,68,68,0.15)'}` }}>
            <div style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.15em', color: 'var(--text-muted)', marginBottom: 4, fontFamily: 'JetBrains Mono' }}>DECISION</div>
            <AnimatePresence mode="wait">
              <motion.div key={decision} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} style={{ fontSize: 22, fontWeight: 900, color: decision === 'ALLOW' ? '#10B981' : decision === 'STEP_UP' ? '#F59E0B' : '#EF4444', fontFamily: 'Space Grotesk' }}>
                {decision === 'STEP_UP' ? 'STEP-UP' : decision}
              </motion.div>
            </AnimatePresence>
          </div>
          <div style={{ padding: 14, borderRadius: 12, background: `${cogColor}06`, border: `1px solid ${cogColor}15` }}>
            <div style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.15em', color: 'var(--text-muted)', marginBottom: 4, fontFamily: 'JetBrains Mono' }}>COGNITIVE STATE</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Brain size={16} color={cogColor} />
              <span style={{ fontSize: 16, fontWeight: 800, color: cogColor, fontFamily: 'Space Grotesk' }}>{cognitiveState.toUpperCase()}</span>
            </div>
          </div>
          <div style={{ padding: 14, borderRadius: 12, background: 'rgba(139,92,246,0.04)', border: '1px solid rgba(139,92,246,0.1)' }}>
            <div style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.15em', color: 'var(--text-muted)', marginBottom: 4, fontFamily: 'JetBrains Mono' }}>ANOMALY SCORE</div>
            <div style={{ fontSize: 16, fontWeight: 800, color: anomalyScore > 0.3 ? '#EF4444' : '#10B981', fontFamily: 'Space Grotesk' }}>{(anomalyScore * 100).toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {/* Pipeline Stepper */}
      <div style={{ background: 'var(--bg-card)', borderRadius: 14, padding: 20, border: '1px solid var(--border-light)', marginBottom: 18 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-main)', marginBottom: 16, fontFamily: 'Space Grotesk' }}>Pipeline Execution Flow</div>
        <Stepper initialStep={1} backButtonText="Previous" nextButtonText="Next">
          <Step>
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Fingerprint size={18} color="#10B981" /></div>
              <div>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px', fontFamily: 'Space Grotesk' }}>Feature Extraction → Embedding</h3>
                <p style={{ fontSize: 11, color: 'var(--text-sub)', margin: 0 }}>16-dim behavioral vector → MiniLM-L6-v2 → 384-dim fingerprint. Latency: ~55ms</p>
              </div>
            </div>
          </Step>
          <Step>
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: 'rgba(59,130,246,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Activity size={18} color="#3B82F6" /></div>
              <div>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px', fontFamily: 'Space Grotesk' }}>Similarity + CUSUM Drift Detection</h3>
                <p style={{ fontSize: 11, color: 'var(--text-sub)', margin: 0 }}>Cosine similarity: {similarity.toFixed(4)} | CUSUM: {driftDetected ? `DRIFT (${driftSeverity})` : 'Normal'}</p>
              </div>
            </div>
          </Step>
          <Step>
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: 'rgba(139,92,246,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Brain size={18} color="#8B5CF6" /></div>
              <div>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px', fontFamily: 'Space Grotesk' }}>Cognitive Classification + Anomaly</h3>
                <p style={{ fontSize: 11, color: 'var(--text-sub)', margin: 0 }}>State: <span style={{ color: cogColor, fontWeight: 700 }}>{cognitiveState.toUpperCase()}</span> | Isolation Forest: {(anomalyScore * 100).toFixed(1)}%</p>
              </div>
            </div>
          </Step>
          <Step>
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: `${trustColor}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Shield size={18} color={trustColor} /></div>
              <div>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px', fontFamily: 'Space Grotesk' }}>Trust Score → Decision</h3>
                <p style={{ fontSize: 11, color: 'var(--text-sub)', margin: 0 }}>T(t) = <span style={{ color: trustColor, fontWeight: 700 }}>{trustScore.toFixed(1)}</span> → <span style={{ color: decision === 'ALLOW' ? '#10B981' : decision === 'STEP_UP' ? '#F59E0B' : '#EF4444', fontWeight: 700 }}>{decision}</span></p>
              </div>
            </div>
          </Step>
        </Stepper>
      </div>

      {/* Intent Vector */}
      <div style={{ background: 'var(--bg-card)', borderRadius: 14, padding: 18, border: '1px solid var(--border-light)' }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-main)', marginBottom: 12, fontFamily: 'Space Grotesk' }}>Fraud Intent Vector</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
          {[
            { label: 'Coercion', value: intentVector.coercion_probability, color: '#EF4444' },
            { label: 'Takeover', value: intentVector.takeover_probability, color: '#F97316' },
            { label: 'Anomaly', value: intentVector.anomaly_severity, color: '#F59E0B' },
            { label: 'Robotic', value: intentVector.robotic_probability, color: '#8B5CF6' },
          ].map(item => (
            <div key={item.label} style={{ padding: '12px 14px', borderRadius: 10, background: `${item.color}05`, border: `1px solid ${item.color}12` }}>
              <div style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: 4, fontFamily: 'JetBrains Mono' }}>{item.label}</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: item.value > 0.5 ? item.color : 'var(--text-sub)', fontFamily: 'Space Grotesk' }}>{(item.value * 100).toFixed(0)}%</div>
              <div style={{ height: 3, background: 'rgba(255,255,255,0.04)', borderRadius: 99, overflow: 'hidden', marginTop: 6 }}>
                <motion.div animate={{ width: `${item.value * 100}%` }} transition={{ duration: 0.6 }} style={{ height: '100%', background: item.color, borderRadius: 99 }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Alert Banner */}
      <AnimatePresence>
        {(cognitiveState === 'panicked' || cognitiveState === 'coerced' || cognitiveState === 'robotic') && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} style={{ background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 12, padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 12, marginTop: 14 }}>
            <AlertTriangle size={18} color="#EF4444" />
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#EF4444', fontFamily: 'Space Grotesk' }}>
                {cognitiveState === 'robotic' ? 'AUTOMATED BEHAVIOR DETECTED' : cognitiveState === 'coerced' ? 'COERCION DETECTED' : 'COGNITIVE DISTRESS'}
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-sub)', marginTop: 2, fontFamily: 'JetBrains Mono' }}>
                {state.reasons.length > 0 ? state.reasons[0] : 'Behavioral anomaly — monitoring escalated.'}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default LiveMonitor
