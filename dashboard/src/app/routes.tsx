import React from 'react'
import { createBrowserRouter, Navigate } from 'react-router'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProtectedLayout from './layout/ProtectedLayout'
import LiveMonitor from './pages/LiveMonitor'
import TrustTimeline from './pages/TrustTimeline'
import CognitiveAnalysis from './pages/CognitiveAnalysis'
import IncidentExplorer from './pages/IncidentExplorer'
import SessionReplay from './pages/SessionReplay'

export const router = createBrowserRouter([
  { path: '/', Component: LandingPage },
  { path: '/login', Component: LoginPage },
  { path: '/register', Component: RegisterPage },
  {
    path: '/app',
    Component: ProtectedLayout,
    children: [
      { index: true, element: <Navigate to="/app/monitor" replace /> },
      { path: 'monitor', Component: LiveMonitor },
      { path: 'timeline', Component: TrustTimeline },
      { path: 'cognitive', Component: CognitiveAnalysis },
      { path: 'incident', Component: IncidentExplorer },
      { path: 'replay', Component: SessionReplay },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
])
