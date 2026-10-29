from __future__ import annotations

import json
import hashlib
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ExecutionDenied(RuntimeError):
    pass


class ExecutionMode(str, Enum):
    REPLAY = "replay"
    LOCAL = "local"
    DEMO = "demo"
    LIVE = "live"


@dataclass(frozen=True)
class ExecutionContext:
    mode: ExecutionMode
    account_id: str | None
    request_id: str


class FakeExecutionAdapter:
    def __init__(self, account_id: str, next_status: str = "accepted"):
        self.account_id = account_id
        self.next_status = next_status
        self.calls: list[tuple] = []

    def place(self, order: dict) -> dict:
        self.calls.append(("place", dict(order)))
        return {
            "status": self.next_status,
            "broker_order_id": "fake-1" if self.next_status == "accepted" else None,
        }

    def close(self, ticket: str) -> dict:
        self.calls.append(("close", str(ticket)))
        return {"status": self.next_status, "broker_order_id": str(ticket)}


class ExecutionJournal:
    """Minimal durable request journal for restart/idempotency experiments."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_requests (
                    request_id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL,
                    account_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    request_fingerprint TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_json TEXT
                )
                """
            )
            connection.commit()

    def _connect(self):
        return sqlite3.connect(self.path)

    def get_record(self, request_id: str) -> dict | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT mode, account_id, operation, request_fingerprint, status, response_json
                FROM execution_requests WHERE request_id = ?
                """,
                (request_id,),
            ).fetchone()
        if row is None:
            return None
        response = json.loads(row[5]) if row[5] else {"status": row[4], "broker_order_id": None}
        return {
            "mode": row[0],
            "account_id": row[1],
            "operation": row[2],
            "request_fingerprint": row[3],
            "response": response,
        }

    def get(self, context: ExecutionContext, operation: str, request_fingerprint: str) -> dict | None:
        record = self.get_record(context.request_id)
        if record is None:
            return None
        expected = (context.mode.value, context.account_id, operation, request_fingerprint)
        actual = (
            record["mode"],
            record["account_id"],
            record["operation"],
            record["request_fingerprint"],
        )
        if actual != expected:
            raise ExecutionDenied("request_id was already used for a different execution intent")
        return dict(record["response"])

    def prepare(self, context: ExecutionContext, operation: str, request_fingerprint: str) -> dict:
        existing = self.get(context, operation, request_fingerprint)
        if existing is not None:
            return existing
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO execution_requests (
                    request_id, mode, account_id, operation, request_fingerprint, status, response_json
                ) VALUES (?, ?, ?, ?, ?, 'unknown', NULL)
                """,
                (
                    context.request_id,
                    context.mode.value,
                    context.account_id,
                    operation,
                    request_fingerprint,
                ),
            )
            connection.commit()
        return {"status": "unknown", "broker_order_id": None}

    def finish(self, request_id: str, result: dict) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                "UPDATE execution_requests SET status = ?, response_json = ? WHERE request_id = ?",
                (result.get("status", "unknown"), json.dumps(result, separators=(",", ":")), request_id),
            )
            connection.commit()

    def reconcile(self, request_id: str, result: dict) -> None:
        if self.get_record(request_id) is None:
            raise KeyError(request_id)
        self.finish(request_id, result)


class ExecutionService:
    """Deny-by-default mode/account gate plus request idempotency."""

    def __init__(self, adapter: FakeExecutionAdapter, journal: ExecutionJournal | None = None):
        self.adapter = adapter
        self.journal = journal
        self._results: dict[str, dict] = {}

    def _guard(self, context: ExecutionContext) -> None:
        if context.mode not in {ExecutionMode.DEMO, ExecutionMode.LIVE}:
            raise ExecutionDenied(f"execution disabled in {context.mode.value} mode")
        if not context.account_id or context.account_id != self.adapter.account_id:
            raise ExecutionDenied("explicit matching account_id is required")
        if not context.request_id.strip():
            raise ExecutionDenied("request_id is required")

    @staticmethod
    def _fingerprint(payload) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def _run_once(self, context: ExecutionContext, operation_name: str, payload, operation) -> dict:
        self._guard(context)
        fingerprint = self._fingerprint(payload)
        if self.journal is not None:
            persisted = self.journal.get(context, operation_name, fingerprint)
            if persisted is not None:
                return dict(persisted)
        cached = self._results.get(context.request_id)
        if cached is not None:
            return dict(cached)
        if self.journal is not None:
            self.journal.prepare(context, operation_name, fingerprint)
        result = operation()
        self._results[context.request_id] = dict(result)
        if self.journal is not None:
            self.journal.finish(context.request_id, result)
        return dict(result)

    def place(self, context: ExecutionContext, order: dict) -> dict:
        return self._run_once(context, "place", order, lambda: self.adapter.place(order))

    def close(self, context: ExecutionContext, ticket: str) -> dict:
        return self._run_once(context, "close", {"ticket": str(ticket)}, lambda: self.adapter.close(ticket))
