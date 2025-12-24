from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, List


@dataclass
class ModerationEvent:
    ts: str
    content_type: str
    decision: str
    flags: Dict[str, Any]
    model_name: str
    mime_type: str
    input_size_bytes: int
    trace_id: str | None = None
    span_id: str | None = None


class InMemoryModerationStore:
    def __init__(self, max_events: int = 5000):
        self.max_events = max_events
        self._lock = Lock()
        self._events: List[ModerationEvent] = []

    def add(self, *, content_type: str, decision: str, flags: Dict[str, Any], model_name: str,
            mime_type: str, input_size_bytes: int, trace_id: str | None, span_id: str | None) -> None:
        ev = ModerationEvent(
            ts=datetime.now(timezone.utc).isoformat(),
            content_type=content_type,
            decision=decision,
            flags=flags,
            model_name=model_name,
            mime_type=mime_type,
            input_size_bytes=input_size_bytes,
            trace_id=trace_id,
            span_id=span_id,
        )
        with self._lock:
            self._events.append(ev)
            if len(self._events) > self.max_events:
                self._events = self._events[-self.max_events :]

    def list_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return [asdict(e) for e in self._events[-limit:]]

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            events = list(self._events)

        total = len(events)
        by_type: Dict[str, int] = {}
        by_decision: Dict[str, int] = {"safe": 0, "unsafe": 0}
        flag_counts: Dict[str, int] = {}

        for e in events:
            by_type[e.content_type] = by_type.get(e.content_type, 0) + 1
            if e.decision in by_decision:
                by_decision[e.decision] += 1

            for k, v in (e.flags or {}).items():
                if v is True:
                    flag_counts[k] = flag_counts.get(k, 0) + 1

        safe_rate = (by_decision["safe"] / total) if total else 0.0
        return {
            "total_events": total,
            "by_type": by_type,
            "by_decision": by_decision,
            "safe_rate": safe_rate,
            "flag_counts_true": dict(sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)),
        }


STORE = InMemoryModerationStore()
