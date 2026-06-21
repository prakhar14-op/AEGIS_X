# AEGIS-X

**Continuous Mathematical Trust Infrastructure & Behavioral Identity Verification for Next-Gen Banking**

## Architecture

```
React Native SDK (TypeScript)
        │ (WebSocket, every 2s)
        ▼
  FastAPI Backend (Python)
        │
        ├── Feature Engineer (16-dim)
        ├── Behavioral Serializer (text description)
        ├── MiniLM Embedding Engine (384-dim fingerprint)
        ├── Cosine Similarity vs Baseline → Drift Score
        ├── CUSUM Drift Detector (gradual + instant jump)
        ├── Cognitive State Machine (Random Forest, 96.3%)
        ├── Trust Score Engine T(t) + Velocity + Acceleration
        └── Decision Engine → ALLOW | STEP_UP | BLOCK
        │
        ├── PostgreSQL (persistent storage)
        └── Redis (session cache, real-time lookups)
        │
        ▼
  Dashboard (Next.js / Streamlit)
```

## Trust Score Formula

```
T(t) = 0.40 × behavioral_similarity
     + 0.20 × device_trust
     + 0.20 × transaction_normality
     + 0.20 × cognitive_stability
```

**Temporal Dynamics:** Trust Velocity (dT/dt), Acceleration (d²T/dt²), Entropy H(t), Drift D(t)

**Decision Thresholds:**
- `[ALLOW]`   T > 0.85 — transaction proceeds
- `[STEP-UP]` T 0.60–0.85 — biometric verification required
- `[BLOCK]`   T < 0.60 — session terminated

## Project Structure

```
AEGIS-X/
├── backend/                         ← FastAPI server + all ML services
│   ├── main.py                      (FastAPI app, WebSocket endpoints)
│   ├── api/                         (REST endpoints)
│   ├── websocket/
│   │   └── socket_manager.py        (connection registry, broadcast hub)
│   ├── services/
│   │   ├── feature_engineering.py   (16-dim feature extraction)
│   │   ├── serializer.py            (numbers → natural language)
│   │   ├── embedding_service.py     (MiniLM → 384-dim fingerprint)
│   │   ├── baseline_service.py      (enrollment, EMA update, persistence)
│   │   ├── similarity_service.py    (cosine similarity + classification)
│   │   ├── history_service.py       (temporal dynamics: dT/dt, d²T/dt²)
│   │   ├── drift_service.py         (CUSUM change-point detection)
│   │   ├── cognitive_service.py     (Random Forest state machine)
│   │   ├── trust_service.py         (T(t) computation + velocity)
│   │   ├── decision_service.py      (ALLOW/STEP_UP/BLOCK + explain)
│   │   ├── risk_service.py          (unified risk aggregation)
│   │   ├── trust_pipeline.py        (orchestrator: one process() call)
│   │   └── session_manager.py       (session lifecycle, state container)
│   ├── models/                      (SQLAlchemy ORM — future)
│   ├── schemas/                     (Pydantic validation — future)
│   └── core/
│       └── config.py                (env vars, weights, thresholds)
│
├── simulators/                      ← Demo event generators (no mobile needed)
│   ├── normal_user.py               (calm browsing + small payment)
│   ├── scam_victim.py               (escalating coercion → BLOCK)
│   └── malware_bot.py               (robotic automation → BLOCK)
│
├── scripts/                         ← Data generation + model training
│   ├── generate_behavioral_data.py  (10,500 samples, 4 scenarios)
│   ├── generate_cognitive_dataset.py (12,000 samples, 6 states)
│   └── train_cognitive_model.py     (Random Forest → 96.3% accuracy)
│
├── tests/                           ← End-to-end pipeline tests
│   ├── test_serializer.py
│   ├── test_embedding_pipeline.py
│   ├── test_baseline.py
│   ├── test_phase3_drift_detection.py
│   ├── test_phase5_trust_engine.py
│   ├── test_phase6_session_manager.py
│   └── test_phase6b_pipeline.py
│
├── data/synthetic/                  ← Generated training datasets
├── models/cognitive/                ← Trained RF model (.pkl)
├── embeddings/baselines/            ← User baseline .npz files
├── aegis-dashboard/                 ← Next.js real-time monitoring UI
├── sdk/                             ← React Native SDK (placeholder)
├── configs/                         ← Configuration files
├── notebooks/                       ← Jupyter experimentation
├── docs/                            ← Documentation
└── requirements/
    └── base.txt                     ← Python dependencies
```

## Quick Start

```bash
# Setup
python -m venv venv
venv\Scripts\activate              # Windows
pip install -r requirements/base.txt

# Generate data + train model
python scripts/generate_behavioral_data.py
python scripts/generate_cognitive_dataset.py
python scripts/train_cognitive_model.py

# Start server
uvicorn backend.main:app --reload

# Run simulators (separate terminals)
python -m simulators.normal_user
python -m simulators.scam_victim
python -m simulators.malware_bot
```

## Demo Scenarios

| Scenario | Trust Pattern | Cognitive State | Decision |
|----------|--------------|-----------------|----------|
| Normal User | T ∈ [0.95, 0.99] | calm/focused | ALLOW |
| Account Takeover | T: 0.99 → 0.87 (drift) | focused | STEP_UP |
| Scam Call Victim | T: 0.95 → 0.50 | panicked → coerced | BLOCK |
| Remote Malware | T drops instantly | robotic | BLOCK |

## Tech Stack

- **Backend:** Python 3.13, FastAPI, WebSocket
- **ML:** sentence-transformers/all-MiniLM-L6-v2, scikit-learn (Random Forest, CUSUM)
- **Databases:** PostgreSQL + Redis
- **Dashboard:** Next.js (aegis-dashboard/)
- **Mobile SDK:** React Native (TypeScript) — placeholder
