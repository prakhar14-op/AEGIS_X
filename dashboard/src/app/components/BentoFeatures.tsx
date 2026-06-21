import React from 'react'
import { motion } from 'motion/react'
import { Shield, Brain, TrendingDown, Fingerprint, Zap, Lock, AlertTriangle, CheckCircle } from 'lucide-react'

const SkeletonTrust = () => (
  <div style={{ padding: '16px', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, marginTop: 8 }}>
    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 4, marginBottom: 12 }}>
      <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'rgba(239,68,68,0.5)' }} />
      <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'rgba(245,158,11,0.5)' }} />
      <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'rgba(16,185,129,0.5)' }} />
    </div>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {[
        { label: 'Behavioral Similarity', value: '94%', color: '#10B981', width: '94%' },
        { label: 'Cognitive Stability', value: '35%', color: '#EF4444', width: '35%' },
        { label: 'Transaction Normal', value: '42%', color: '#F59E0B', width: '42%' },
      ].map((bar, i) => (
        <div key={i}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'rgba(255,255,255,0.5)', fontFamily: 'JetBrains Mono', marginBottom: 4 }}>
            <span>{bar.label}</span><span>{bar.value}</span>
          </div>
          <div style={{ height: 6, width: '100%', background: 'rgba(255,255,255,0.04)', borderRadius: 4, overflow: 'hidden' }}>
            <motion.div initial={{ width: 0 }} whileInView={{ width: bar.width }} transition={{ duration: 1.2, delay: i * 0.2 }} viewport={{ once: true }}
              style={{ height: '100%', background: bar.color, borderRadius: 4 }} />
          </div>
        </div>
      ))}
    </div>
  </div>
)

const SkeletonDrift = () => (
  <div style={{ padding: 12, marginTop: 8 }}>
    <svg viewBox="0 0 300 80" style={{ width: '100%', height: 80 }}>
      <defs>
        <linearGradient id="driftLine" x1="0" x2="1">
          <stop offset="0%" stopColor="#10B981" />
          <stop offset="60%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#EF4444" />
        </linearGradient>
      </defs>
      <line x1="0" y1="20" x2="300" y2="20" stroke="rgba(16,185,129,0.2)" strokeWidth="1" strokeDasharray="3,3" />
      <text x="270" y="16" fill="rgba(16,185,129,0.5)" fontSize="7" fontFamily="JetBrains Mono">ALLOW</text>
      <line x1="0" y1="50" x2="300" y2="50" stroke="rgba(239,68,68,0.2)" strokeWidth="1" strokeDasharray="3,3" />
      <text x="270" y="46" fill="rgba(239,68,68,0.5)" fontSize="7" fontFamily="JetBrains Mono">BLOCK</text>
      <polyline points="0,18 30,17 60,19 90,22 120,28 150,35 180,42 210,50 240,58 270,64 300,68"
        stroke="url(#driftLine)" strokeWidth="2.5" fill="none" strokeLinecap="round" />
      {[90, 150, 210].map((x, i) => (
        <circle key={i} cx={x} cy={[22, 35, 50][i]} r="3" fill={['#F59E0B', '#F97316', '#EF4444'][i]} />
      ))}
    </svg>
    <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
      <span style={{ fontSize: 9, color: '#F59E0B', background: 'rgba(245,158,11,0.1)', padding: '2px 8px', borderRadius: 10, fontFamily: 'JetBrains Mono', border: '1px solid rgba(245,158,11,0.2)' }}>DRIFT DETECTED</span>
      <span style={{ fontSize: 9, color: '#EF4444', background: 'rgba(239,68,68,0.1)', padding: '2px 8px', borderRadius: 10, fontFamily: 'JetBrains Mono', border: '1px solid rgba(239,68,68,0.2)' }}>CUSUM: 0.42</span>
    </div>
  </div>
)

const SkeletonSecurity = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
    {[
      { label: 'Anti-Poisoning Gate', desc: 'Baseline updates only when T > 0.90', color: '#10B981' },
      { label: 'EMA Adaptation', desc: 'Concept drift handled with decay=0.95', color: '#3B82F6' },
      { label: 'Zero Raw Exposure', desc: 'Only embeddings leave device scope', color: '#8B5CF6' },
    ].map((item, i) => (
      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 8 }}>
        <div style={{ width: 6, height: 6, borderRadius: '50%', background: item.color, boxShadow: `0 0 6px ${item.color}` }} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.85)', fontFamily: 'Space Grotesk' }}>{item.label}</div>
          <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)' }}>{item.desc}</div>
        </div>
        <CheckCircle size={14} color={item.color} />
      </div>
    ))}
  </div>
)

const SkeletonCognitive = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8 }}>
    <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
        <span style={{ fontSize: 10, color: '#8B5CF6', fontFamily: 'JetBrains Mono', fontWeight: 600 }}>AI CLASSIFIER</span>
      </div>
      <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>
        State detected: <strong style={{ color: '#EF4444' }}>PANICKED</strong>
        <br />Hesitation +340% · Corrections +4x baseline
      </div>
    </div>
    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
      {['CALM', 'FOCUSED', 'DISTRESSED', 'PANICKED', 'COERCED', 'ROBOTIC'].map((s, i) => (
        <span key={s} style={{ fontSize: 8, padding: '2px 6px', borderRadius: 8, fontFamily: 'JetBrains Mono', fontWeight: 500,
          color: i === 3 ? '#EF4444' : 'rgba(255,255,255,0.35)',
          background: i === 3 ? 'rgba(239,68,68,0.12)' : 'rgba(255,255,255,0.03)',
          border: `1px solid ${i === 3 ? 'rgba(239,68,68,0.3)' : 'rgba(255,255,255,0.06)'}`,
        }}>{s}</span>
      ))}
    </div>
  </div>
)

export default function BentoFeatures() {
  const features = [
    {
      badge: 'TRUST ENGINE', badgeColor: '#10B981',
      title: 'Real-Time Trust Scoring',
      desc: 'T(t) = 0.40×Sim + 0.20×Device + 0.20×Tx + 0.20×Cognitive. Computed every 2 seconds.',
      skeleton: <SkeletonTrust />,
      className: 'col-span-4 border-b border-r',
    },
    {
      badge: 'DRIFT', badgeColor: '#F59E0B',
      title: 'CUSUM Change-Point Detection',
      desc: 'Catches gradual account takeover that single-threshold checks miss entirely.',
      skeleton: <SkeletonDrift />,
      className: 'col-span-2 border-b',
    },
    {
      badge: 'COGNITIVE', badgeColor: '#3B82F6',
      title: 'State Machine Classifier',
      desc: 'Random Forest (96.3% accuracy) detects coercion, panic, and automation patterns.',
      skeleton: <SkeletonCognitive />,
      className: 'col-span-3 border-r',
    },
    {
      badge: 'SECURITY', badgeColor: '#8B5CF6',
      title: 'Enterprise-Grade Architecture',
      desc: 'Zero-PII, anti-poisoning gates, and deterministic fallbacks built for banking compliance.',
      skeleton: <SkeletonSecurity />,
      className: 'col-span-3',
    },
  ]

  return (
    <div style={{ position: 'relative', zIndex: 20, padding: '80px 0', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ padding: '0 32px', textAlign: 'center', marginBottom: 48 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.18)', borderRadius: 20, padding: '5px 14px', marginBottom: 20 }}>
          <Zap size={11} color="#10B981" />
          <span style={{ fontSize: 11, color: '#10B981', fontFamily: 'JetBrains Mono', letterSpacing: '0.08em' }}>THE PLATFORM</span>
        </div>
        <h2 style={{ fontSize: 44, fontWeight: 700, color: 'var(--text-main)', fontFamily: 'Space Grotesk, sans-serif', letterSpacing: '-0.03em', margin: '0 0 14px', lineHeight: 1.1 }}>
          Built for <span style={{ color: '#10B981' }}>Precision</span>
        </h2>
        <p style={{ fontSize: 16, color: 'var(--text-sub)', maxWidth: 520, margin: '0 auto', lineHeight: 1.7 }}>
          Every feature is engineered for real-time security, not complexity.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, background: 'rgba(0,0,0,0.25)', overflow: 'hidden', margin: '0 32px' }}>
        {features.map((f, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            style={{ padding: 28, gridColumn: f.className.includes('col-span-4') ? 'span 4' : f.className.includes('col-span-3') ? 'span 3' : 'span 2', borderBottom: f.className.includes('border-b') ? '1px solid rgba(255,255,255,0.07)' : 'none', borderRight: f.className.includes('border-r') ? '1px solid rgba(255,255,255,0.07)' : 'none' }}
          >
            <span style={{ fontSize: 9, letterSpacing: '0.12em', color: f.badgeColor, fontFamily: 'JetBrains Mono', fontWeight: 600, textTransform: 'uppercase' }}>{f.badge}</span>
            <h3 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-main)', fontFamily: 'Space Grotesk', margin: '8px 0 6px', lineHeight: 1.2 }}>{f.title}</h3>
            <p style={{ fontSize: 13, color: 'var(--text-sub)', lineHeight: 1.6, maxWidth: 400 }}>{f.desc}</p>
            {f.skeleton}
          </motion.div>
        ))}
      </div>
    </div>
  )
}
