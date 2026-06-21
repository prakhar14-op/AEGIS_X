import React from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router'
import { motion, AnimatePresence } from 'motion/react'
import {
  Activity, Radio, TrendingDown, Brain, FileWarning, RotateCcw,
  PanelLeftClose, PanelLeftOpen, Shield, ChevronLeft, LogOut,
} from 'lucide-react'
import { logout, getUsername } from '../../services/auth'

const navItems = [
  { icon: <Radio size={17} />, label: 'Live Monitor', path: '/app/monitor', desc: 'Real-time trust' },
  { icon: <TrendingDown size={17} />, label: 'Trust Timeline', path: '/app/timeline', desc: 'Score history' },
  { icon: <Brain size={17} />, label: 'Cognitive Analysis', path: '/app/cognitive', desc: 'State machine' },
  { icon: <FileWarning size={17} />, label: 'Incident Explorer', path: '/app/incident', desc: 'Root causes' },
  { icon: <RotateCcw size={17} />, label: 'Session Replay', path: '/app/replay', desc: 'Attack timeline' },
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const location = useLocation()

  return (
    <motion.aside
      animate={{ width: collapsed ? 68 : 252 }}
      transition={{ type: 'spring', stiffness: 320, damping: 32 }}
      className="glass-panel"
      style={{
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        overflow: 'hidden',
        borderRight: '1px solid var(--border-light)',
        background: 'var(--bg-elevated)',
      }}
    >
      {/* Logo */}
      <div style={{
        padding: collapsed ? '18px 10px' : '22px 18px',
        borderBottom: '1px solid var(--border-light)',
        display: 'flex',
        alignItems: collapsed ? 'center' : 'flex-start',
        justifyContent: collapsed ? 'center' : 'space-between',
        minHeight: 76,
        flexDirection: collapsed ? 'column' : 'row',
        gap: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 9,
            background: 'linear-gradient(135deg, #10b981, #059669)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 18px rgba(16,185,129,0.25), inset 0 1px 1px rgba(255,255,255,0.1)',
            flexShrink: 0,
          }}>
            <Shield size={17} color="white" />
          </div>
          {!collapsed && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <span className="heading" style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-main)', display: 'block', lineHeight: 1.2 }}>AEGIS-X</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginTop: 3 }}>
                <div className="animate-pulse-glow" style={{ width: 5, height: 5, borderRadius: '50%', background: '#10b981', color: '#10b981' }} />
                <span className="mono" style={{ fontSize: 9, color: 'var(--text-muted)', letterSpacing: '0.05em' }}>TRUST ENGINE ACTIVE</span>
              </div>
            </motion.div>
          )}
        </div>
        <button onClick={onToggle} title={collapsed ? 'Expand' : 'Collapse'} style={{
          background: 'var(--accent-primary-dim)', border: '1px solid rgba(16,185,129,0.12)',
          borderRadius: 7, padding: 6, cursor: 'pointer', display: 'flex',
          alignItems: 'center', justifyContent: 'center', color: '#10b981',
          transition: 'all var(--transition-fast)',
        }}>
          {collapsed ? <PanelLeftOpen size={14} /> : <PanelLeftClose size={14} />}
        </button>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: collapsed ? '14px 10px' : '18px 12px', display: 'flex', flexDirection: 'column', gap: 3, overflowY: 'auto' }}>
        {!collapsed && (
          <div className="label-xs" style={{ padding: '4px 10px 12px' }}>Monitoring</div>
        )}
        {navItems.map(item => {
          const isActive = location.pathname === item.path
          return (
            <NavLink key={item.path} to={item.path} style={{ textDecoration: 'none' }}>
              <motion.div
                whileHover={{ x: collapsed ? 0 : 2, backgroundColor: isActive ? undefined : 'rgba(148,163,184,0.04)' }}
                style={{
                  display: 'flex', alignItems: 'center', gap: collapsed ? 0 : 11,
                  padding: collapsed ? '11px 0' : '10px 12px',
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  borderRadius: 'var(--radius-sm)',
                  background: isActive ? 'var(--accent-primary-dim)' : 'transparent',
                  border: isActive ? '1px solid rgba(16,185,129,0.15)' : '1px solid transparent',
                  cursor: 'pointer', transition: 'all var(--transition-fast)', position: 'relative',
                }}
              >
                {isActive && !collapsed && (
                  <motion.div layoutId="nav-indicator" style={{ position: 'absolute', left: 0, top: '18%', bottom: '18%', width: 2.5, borderRadius: 2, background: '#10b981', boxShadow: '0 0 8px rgba(16,185,129,0.5)' }} />
                )}
                <div style={{ color: isActive ? '#10b981' : 'var(--text-muted)', display: 'flex', flexShrink: 0, transition: 'color var(--transition-fast)' }}>
                  {item.icon}
                </div>
                <AnimatePresence>
                  {!collapsed && (
                    <motion.div
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: 'auto' }}
                      exit={{ opacity: 0, width: 0 }}
                      transition={{ duration: 0.15 }}
                      style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}
                    >
                      <div className="heading" style={{ fontSize: 13, fontWeight: 550, color: isActive ? 'var(--text-main)' : 'var(--text-sub)', lineHeight: 1.2 }}>{item.label}</div>
                      <div className="mono" style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{item.desc}</div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{ padding: '14px 12px', borderTop: '1px solid var(--border-light)' }}>
        {!collapsed && (
          <div style={{
            background: 'rgba(16,185,129,0.04)', border: '1px solid rgba(16,185,129,0.08)',
            borderRadius: 'var(--radius-sm)', padding: '11px 13px',
          }}>
            <div className="label-xs" style={{ marginBottom: 5 }}>PIPELINE STATUS</div>
            <div className="mono" style={{ fontSize: 11, color: '#10b981', fontWeight: 600 }}>All Services Operational</div>
            <div className="mono" style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 3 }}>Latency: ~65ms • Uptime: 100%</div>
          </div>
        )}
        {!collapsed && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 10px 4px', marginTop: 8 }}>
            <div>
              <div className="heading" style={{ fontSize: 12, color: 'var(--text-sub)', fontWeight: 600 }}>{getUsername() || 'User'}</div>
              <div className="mono" style={{ fontSize: 9, color: 'var(--text-muted)' }}>Analyst</div>
            </div>
            <button onClick={() => logout()} title="Sign out"
              style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 6, padding: 6, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#EF4444', transition: 'all 0.2s' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.15)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.3)' }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.08)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.15)' }}>
              <LogOut size={13} />
            </button>
          </div>
        )}
        {collapsed && (
          <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 8 }}>
            <button onClick={() => logout()} title="Sign out"
              style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 6, padding: 6, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#EF4444' }}>
              <LogOut size={13} />
            </button>
          </div>
        )}
      </div>
    </motion.aside>
  )
}

export default Sidebar
