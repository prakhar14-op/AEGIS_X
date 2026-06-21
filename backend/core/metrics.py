import time
from collections import defaultdict, deque
from typing import Dict, List
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class LatencyBucket:
    samples: deque = field(default_factory=lambda: deque(maxlen=1000))
    total: float = 0.0
    count: int = 0

    def record(self, value: float):
        self.samples.append(value)
        self.total += value
        self.count += 1

    @property
    def mean(self) -> float:
        if not self.samples:
            return 0.0
        return sum(self.samples) / len(self.samples)

    @property
    def p50(self) -> float:
        if not self.samples:
            return 0.0
        sorted_s = sorted(self.samples)
        return sorted_s[len(sorted_s) // 2]

    @property
    def p95(self) -> float:
        if not self.samples:
            return 0.0
        sorted_s = sorted(self.samples)
        idx = int(len(sorted_s) * 0.95)
        return sorted_s[min(idx, len(sorted_s) - 1)]

    @property
    def p99(self) -> float:
        if not self.samples:
            return 0.0
        sorted_s = sorted(self.samples)
        idx = int(len(sorted_s) * 0.99)
        return sorted_s[min(idx, len(sorted_s) - 1)]


class MetricsCollector:

    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._counters: Dict[str, int] = defaultdict(int)
        self._latencies: Dict[str, LatencyBucket] = defaultdict(LatencyBucket)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._start_time = time.time()
        self._decision_counts: Dict[str, int] = defaultdict(int)
        self._cognitive_state_counts: Dict[str, int] = defaultdict(int)
        self._alert_counts: Dict[str, int] = defaultdict(int)

    def increment(self, name: str, value: int = 1):
        self._counters[name] += value

    def record_latency(self, name: str, value_ms: float):
        self._latencies[name].record(value_ms)

    def set_gauge(self, name: str, value: float):
        self._gauges[name] = value

    def record_decision(self, decision: str):
        self._decision_counts[decision] += 1
        self._counters["total_decisions"] += 1

    def record_cognitive_state(self, state: str):
        self._cognitive_state_counts[state] += 1

    def record_alert(self, severity: str):
        self._alert_counts[severity] += 1
        self._counters["total_alerts"] += 1

    def snapshot(self) -> Dict:
        uptime = time.time() - self._start_time
        pipeline_latency = self._latencies.get("pipeline", LatencyBucket())
        return {
            "uptime_seconds": round(uptime, 1),
            "counters": {
                "total_events_processed": self._counters.get("total_events", 0),
                "total_decisions": self._counters.get("total_decisions", 0),
                "total_alerts": self._counters.get("total_alerts", 0),
                "total_sessions": self._counters.get("total_sessions", 0),
                "total_blocks": self._decision_counts.get("BLOCK", 0),
                "total_step_ups": self._decision_counts.get("STEP_UP", 0),
            },
            "latency_ms": {
                "pipeline_mean": round(pipeline_latency.mean, 2),
                "pipeline_p50": round(pipeline_latency.p50, 2),
                "pipeline_p95": round(pipeline_latency.p95, 2),
                "pipeline_p99": round(pipeline_latency.p99, 2),
            },
            "decisions": dict(self._decision_counts),
            "cognitive_states": dict(self._cognitive_state_counts),
            "alerts_by_severity": dict(self._alert_counts),
            "gauges": dict(self._gauges),
        }

    def reset(self):
        self._counters.clear()
        self._latencies.clear()
        self._gauges.clear()
        self._decision_counts.clear()
        self._cognitive_state_counts.clear()
        self._alert_counts.clear()
        self._start_time = time.time()


metrics = MetricsCollector()
