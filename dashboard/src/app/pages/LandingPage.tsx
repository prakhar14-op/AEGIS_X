import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { motion } from 'motion/react'
import {
  ArrowRight, Shield, Brain, Activity, Fingerprint, Eye,
  ChevronRight, Sparkles, Layers, Radio, Settings,
  CheckCircle, Zap, Lock, TrendingDown, AlertTriangle,
} from 'lucide-react'
import CardSwap, { Card } from '../components/CardSwap'
import { Card1, Card2, Card3, Card4, Card5 } from '../components/LandingCards'
import BentoFeatures from '../components/BentoFeatures'

const LandingPage: React.FC = () => {
  const navigate = useNavigate()
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const heroRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (heroRef.current) {
        const r = heroRef.current.getBoundingClientRect()
        setMousePos({ x: e.clientX - r.left, y: e.clientY - r.top })
      }
    }
    window.addEventListener('mousemove', h)
    return () => window.removeEventListener('mousemove', h)
  }, [])

  return (
    <div style={{ background: 'var(--bg-page)', minHeight: '100vh', color: 'var(--text-main)', fontFamily: 'Inter, sans-serif', overflowX: 'hidden' }}>

      {/* Navbar — exact FinSight structure */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, background: 'var(--bg-panel-trans, rgba(6,11,24,0.85))', backdropFilter: 'blur(20px)', borderBottom: '1px solid var(--border-light)', padding: '0 40px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: '0 1px 16px rgba(16,185,129,0.06)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'linear-gradient(135deg, #10B981, #059669)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 16px rgba(16,185,129,0.3)' }}>
            <Shield size={16} color="white" />
          </div>
          <span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)', fontFamily: 'Space Grotesk, sans-serif', letterSpacing: '-0.02em' }}>AEGIS-X</span>
          <span style={{ fontSize: '10px', color: '#10B981', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.22)', padding: '2px 8px', borderRadius: '20px', fontFamily: 'JetBrains Mono', letterSpacing: '0.05em' }}>v2.0</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          {['Architecture', 'Features', 'Dashboard'].map(item => (
            <button key={item} onClick={() => navigate('/app/monitor')} style={{ background: 'none', border: 'none', color: 'var(--text-sub)', cursor: 'pointer', padding: '4px 0', transition: 'color 0.2s', fontSize: '14px', fontWeight: 500 }}
              onMouseEnter={e => (e.currentTarget.style.color = '#10B981')}
              onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-sub)')}>
              {item}
            </button>
          ))}
          <button onClick={() => navigate('/app/monitor')} style={{ background: 'linear-gradient(135deg, #10B981, #059669)', border: 'none', color: 'white', padding: '8px 20px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 0.2s', fontFamily: 'Inter, sans-serif', boxShadow: '0 0 20px rgba(16,185,129,0.25)', fontSize: '14px', fontWeight: 500 }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 4px 24px rgba(16,185,129,0.45)' }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = '0 0 20px rgba(16,185,129,0.25)' }}>
            Enter Dashboard <ArrowRight size={14} />
          </button>
        </div>
      </nav>

      {/* Hero Section — exact FinSight grid */}
      <section ref={heroRef} style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', paddingTop: '64px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(16,185,129,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(16,185,129,0.04) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />
          <div style={{ position: 'absolute', top: '15%', left: '8%', width: '500px', height: '500px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(16,185,129,0.1) 0%, transparent 70%)', filter: 'blur(40px)' }} />
          <div style={{ position: 'absolute', bottom: '10%', right: '20%', width: '400px', height: '400px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 70%)', filter: 'blur(40px)' }} />
          <div style={{ position: 'absolute', width: '300px', height: '300px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(16,185,129,0.05) 0%, transparent 70%)', transform: `translate(${mousePos.x - 150}px, ${mousePos.y - 150}px)`, transition: 'transform 0.3s ease', pointerEvents: 'none' }} />
        </div>

        <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 40px', width: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '60px', alignItems: 'center', position: 'relative', zIndex: 1 }}>
          {/* LEFT */}
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: 'easeOut' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '20px', padding: '6px 14px', marginBottom: '28px' }}>
              <Sparkles size={12} color="#10B981" />
              <span style={{ fontSize: '12px', color: '#10B981', fontFamily: 'JetBrains Mono', fontWeight: 500 }}>Cyber Security PSBs Hackathon 2026</span>
            </div>

            <h1 style={{ fontSize: '58px', fontWeight: 700, color: 'var(--text-main)', fontFamily: 'Space Grotesk, sans-serif', lineHeight: '1.1', letterSpacing: '-0.03em', margin: '0 0 20px 0' }}>
              Continuous Trust<br />
              <span style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 50%, #06B6D4 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                Infrastructure
              </span>
            </h1>

            <p style={{ fontSize: '18px', color: 'var(--text-sub)', lineHeight: '1.7', margin: '0 0 36px', maxWidth: '520px' }}>
              AEGIS-X replaces one-time passwords with a living mathematical system — behavioral embeddings, CUSUM drift detection, and cognitive state analysis that terminate sessions the millisecond they drift.
            </p>

            <div style={{ display: 'flex', gap: '32px', marginBottom: '40px' }}>
              {[
                { val: '<100ms', label: 'Trust Latency' },
                { val: '96.3%', label: 'Cognitive Accuracy' },
                { val: '384-D', label: 'Embedding Space' },
              ].map((stat, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 + i * 0.1 }}>
                  <div style={{ fontSize: '26px', fontWeight: 700, color: 'var(--text-main)', fontFamily: 'Space Grotesk, sans-serif', lineHeight: 1 }}>{stat.val}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'JetBrains Mono' }}>{stat.label}</div>
                </motion.div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
              <motion.button onClick={() => navigate('/app/monitor')} whileHover={{ scale: 1.03, boxShadow: '0 8px 40px rgba(16,185,129,0.45)' }} whileTap={{ scale: 0.98 }}
                style={{ background: 'linear-gradient(135deg, #10B981, #059669)', border: 'none', color: 'white', padding: '14px 28px', borderRadius: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'Space Grotesk, sans-serif', fontWeight: 600, boxShadow: '0 0 30px rgba(16,185,129,0.3)', fontSize: '15px' }}>
                Open Dashboard <ArrowRight size={16} />
              </motion.button>
              <motion.button onClick={() => navigate('/app/incident')} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-light)', color: 'var(--text-sub)', padding: '14px 28px', borderRadius: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'Space Grotesk, sans-serif', fontWeight: 500, fontSize: '15px', transition: 'all 0.2s', boxShadow: '0 2px 8px rgba(0,0,0,0.2)' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(16,185,129,0.4)'; e.currentTarget.style.color = '#10B981' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-light)'; e.currentTarget.style.color = 'var(--text-sub)' }}>
                Explore Features <ChevronRight size={16} />
              </motion.button>
            </div>

            <div style={{ display: 'flex', gap: '20px', marginTop: '36px', alignItems: 'center' }}>
              {['Zero-Day Detection', 'Anti-Coercion', 'Bank-Grade'].map((badge, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <CheckCircle size={12} color="#059669" />
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>{badge}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* RIGHT: CardSwap */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, delay: 0.3 }} style={{ position: 'relative', height: '560px', display: 'flex', justifyContent: 'center' }}>
            <div style={{ position: 'relative', height: '560px', width: '100%' }}>
              <CardSwap width={460} height={340} cardDistance={55} verticalDistance={65} delay={4500} pauseOnHover={true} skewAmount={5}>
                <Card><Card1 /></Card>
                <Card><Card2 /></Card>
                <Card><Card3 /></Card>
                <Card><Card4 /></Card>
                <Card><Card5 /></Card>
              </CardSwap>
            </div>
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <div style={{ position: 'absolute', bottom: '32px', left: '50%', transform: 'translateX(-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', zIndex: 1 }}>
          <span style={{ fontSize: '10px', color: '#9CA3AF', letterSpacing: '0.12em', fontFamily: 'JetBrains Mono' }}>SCROLL TO EXPLORE</span>
          <motion.div animate={{ y: [0, 6, 0] }} transition={{ repeat: Infinity, duration: 1.8 }} style={{ width: '1px', height: '30px', background: 'linear-gradient(to bottom, rgba(16,185,129,0.5), transparent)' }} />
        </div>
      </section>

      {/* Features — Bento Grid (NxtDevs-inspired) */}
      <section style={{ padding: '40px 0', background: 'var(--bg-panel, #12151E)', position: 'relative' }}>
        <BentoFeatures />
      </section>

      {/* Architecture Strip — exact FinSight 5-col pattern */}
      <section style={{ padding: '80px 40px', position: 'relative', background: 'var(--bg-page)' }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '48px' }}>
            <h2 style={{ fontSize: '32px', fontWeight: 700, color: 'var(--text-main)', fontFamily: 'Space Grotesk, sans-serif', letterSpacing: '-0.02em', margin: '0 0 12px' }}>How It Works</h2>
            <p style={{ fontSize: '15px', color: 'var(--text-sub)', margin: 0 }}>Three-layer architecture: Capture → Analyze → Decide</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr auto 1fr', gap: '0', alignItems: 'center' }}>
            {[
              { label: 'SDK Capture', sub: 'Behavioral telemetry every 2s', color: '#3B82F6', icon: <Radio size={24} /> },
              null,
              { label: 'AI Engine', sub: 'Embedding + CUSUM + RF classifier', color: '#10B981', icon: <Brain size={24} /> },
              null,
              { label: 'Trust Decision', sub: 'ALLOW / STEP-UP / BLOCK', color: '#EF4444', icon: <Shield size={24} /> },
            ].map((item, i) =>
              item === null ? (
                <div key={i} style={{ display: 'flex', justifyContent: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                    {[0, 1, 2, 3].map(d => (
                      <motion.div key={d} animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.5, delay: d * 0.2 }} style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#10B981' }} />
                    ))}
                  </div>
                </div>
              ) : (
                <motion.div key={i} initial={{ opacity: 0, scale: 0.9 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                  style={{ background: 'var(--bg-panel)', border: `1px solid ${item.color}22`, borderRadius: '14px', padding: '28px', textAlign: 'center', boxShadow: '0 4px 16px rgba(0,0,0,0.2)' }}>
                  <div style={{ color: item.color, display: 'flex', justifyContent: 'center', marginBottom: '12px' }}>{item.icon}</div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px', fontFamily: 'Space Grotesk, sans-serif' }}>{item.label}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>{item.sub}</div>
                </motion.div>
              )
            )}
          </div>
        </div>
      </section>

      {/* CTA Section — exact FinSight structure */}
      <section style={{ padding: '100px 40px', position: 'relative', overflow: 'hidden', background: 'var(--bg-panel, #0c1222)' }}>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '600px', height: '400px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%)', filter: 'blur(60px)', pointerEvents: 'none' }} />
        <div style={{ maxWidth: '700px', margin: '0 auto', textAlign: 'center', position: 'relative' }}>
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2 style={{ fontSize: '48px', fontWeight: 700, color: 'var(--text-main)', fontFamily: 'Space Grotesk, sans-serif', letterSpacing: '-0.02em', margin: '0 0 20px' }}>
              Ready to see<br />
              <span style={{ background: 'linear-gradient(135deg, #10B981, #059669)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                trust in action?
              </span>
            </h2>
            <p style={{ fontSize: '16px', color: 'var(--text-sub)', margin: '0 0 40px', lineHeight: '1.7' }}>
              Launch the Security Operations Center, simulate attack scenarios, and watch AEGIS-X detect coercion, takeover, and malware in real-time.
            </p>
            <div style={{ display: 'flex', gap: '14px', justifyContent: 'center' }}>
              <motion.button onClick={() => navigate('/app/monitor')} whileHover={{ scale: 1.04, boxShadow: '0 12px 50px rgba(16,185,129,0.45)' }} whileTap={{ scale: 0.97 }}
                style={{ background: 'linear-gradient(135deg, #10B981, #059669)', border: 'none', color: 'white', padding: '16px 36px', borderRadius: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'Space Grotesk, sans-serif', fontWeight: 600, boxShadow: '0 0 40px rgba(16,185,129,0.3)', fontSize: '16px' }}>
                Launch SOC Dashboard <ArrowRight size={18} />
              </motion.button>
              <motion.button onClick={() => navigate('/app/replay')} whileHover={{ scale: 1.02 }}
                style={{ background: 'var(--bg-page)', border: '1px solid var(--border-light)', color: 'var(--text-sub)', padding: '16px 28px', borderRadius: '12px', cursor: 'pointer', fontFamily: 'Space Grotesk, sans-serif', fontWeight: 500, fontSize: '16px', transition: 'all 0.2s' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(16,185,129,0.3)'; e.currentTarget.style.color = '#10B981' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-light)'; e.currentTarget.style.color = 'var(--text-sub)' }}>
                Watch Attack Demo
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer — exact FinSight structure */}
      <footer style={{ borderTop: '1px solid var(--border-light)', padding: '30px 40px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-page)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Shield size={16} color="#10B981" />
          <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)', fontFamily: 'Space Grotesk, sans-serif' }}>AEGIS-X</span>
          <span style={{ fontSize: '12px', color: '#9CA3AF' }}>· Continuous Trust Infrastructure</span>
        </div>
        <div style={{ display: 'flex', gap: '24px' }}>
          {['DFS & IBA Initiative', 'Central Bank of India', 'MNNIT Allahabad'].map((item, i) => (
            <span key={i} style={{ fontSize: '12px', color: '#9CA3AF', cursor: 'pointer', transition: 'color 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.color = 'var(--text-sub)')}
              onMouseLeave={e => (e.currentTarget.style.color = '#9CA3AF')}>
              {item}
            </span>
          ))}
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
