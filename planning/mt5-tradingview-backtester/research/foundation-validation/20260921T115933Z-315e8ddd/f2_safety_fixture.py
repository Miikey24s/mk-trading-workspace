from __future__ import annotations

import copy
import hashlib
import json
import threading
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Callable, Iterable


IDEMPOTENCY_HOURS = 72
SEEDS = (3, 7, 11, 29)


def _canonical_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "__dataclass_fields__"):
        return {name: _canonical_value(getattr(value, name)) for name in value.__dataclass_fields__}
    if isinstance(value, dict):
        return {str(key): _canonical_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    return value


def canonical_hash(value: Any) -> str:
    body = json.dumps(_canonical_value(value), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


class SafetyError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


class InjectedCrash(RuntimeError):
    pass


@dataclass(frozen=True)
class AccountBinding:
    broker: str
    server: str
    account: str
    mode: str


@dataclass
class Intent:
    intent_id: str
    workspace_id: str
    key: str
    payload_hash: str
    binding: AccountBinding
    contract_version: str
    risk: Decimal
    owner_epoch: int
    state: str = "received"
    revision: int = 1
    dispatch_token: str | None = None
    outcome: str | None = None
    terminal_at: int | None = None
    valid_until: int | None = None
    recovery_log: list[str] = field(default_factory=list)


class FakeBroker:
    """Deterministic fake. Send log is intentionally independent of durable intent state."""

    def __init__(self, *, can_prove_absence: bool = True) -> None:
        self.can_prove_absence = can_prove_absence
        self.send_log: list[dict[str, str]] = []
        self.evidence: dict[str, str] = {}

    def send(self, token: str, outcome: str = "accepted") -> str:
        self.send_log.append({"token": token, "outcome": outcome})
        self.evidence[token] = outcome
        return outcome

    def query(self, token: str) -> str:
        if token in self.evidence:
            return self.evidence[token]
        return "absent" if self.can_prove_absence else "unprovable_absence"

    def send_count(self, token: str | None = None) -> int:
        if token is None:
            return len(self.send_log)
        return sum(1 for item in self.send_log if item["token"] == token)


class IndependentOracle:
    @staticmethod
    def risk_acceptance(order: Iterable[tuple[str, Decimal]], limit: Decimal) -> tuple[list[str], Decimal]:
        accepted: list[str] = []
        total = Decimal("0")
        for intent_id, amount in order:
            if total + amount <= limit:
                accepted.append(intent_id)
                total += amount
        return accepted, total

    @staticmethod
    def reconcile(
        events: Iterable[dict[str, Any]],
        order_qty: Decimal,
        *,
        root_order_id: str = "o1",
    ) -> dict[str, Any]:
        timeline = sorted((copy.deepcopy(event) for event in events), key=lambda event: int(event["seq"]))
        orders: dict[str, dict[str, Any]] = {
            root_order_id: {"status": "open", "target_qty": order_qty, "replaced_by": None}
        }
        active_order = root_order_id
        latest_deals: dict[str, dict[str, Any]] = {}
        for event in timeline:
            if event["kind"] == "replace":
                if event["order_id"] != active_order or Decimal(str(event["new_qty"])) <= 0:
                    raise SafetyError("RECONCILE_INVALID_REPLACE")
                orders[active_order]["status"] = "replaced"
                orders[active_order]["replaced_by"] = event["new_order_id"]
                active_order = event["new_order_id"]
                orders[active_order] = {
                    "status": "open",
                    "target_qty": Decimal(str(event["new_qty"])),
                    "replaced_by": None,
                }
            elif event["kind"] == "cancel" and event["order_id"] in orders:
                orders[event["order_id"]]["status"] = "canceled"
            elif event["kind"] in {"fill", "correction"}:
                current = latest_deals.get(event["deal_id"])
                if current is None or int(event["version"]) > int(current["version"]):
                    latest_deals[event["deal_id"]] = event

        deals = [
            {
                "deal_id": deal_id,
                "order_id": event["order_id"],
                "version": int(event["version"]),
                "qty": Decimal(str(event["qty"])),
                "fee": Decimal(str(event["fee"])),
            }
            for deal_id, event in sorted(latest_deals.items())
        ]
        qty = sum((deal["qty"] for deal in deals), Decimal("0"))
        fees = sum((deal["fee"] for deal in deals), Decimal("0"))
        target_qty = Decimal(str(orders[active_order]["target_qty"]))
        canceled = orders[active_order]["status"] == "canceled"
        if qty >= target_qty:
            status = "filled"
        elif qty > 0 and canceled:
            status = "partially_filled_canceled"
        elif qty > 0:
            status = "partially_filled"
        elif canceled:
            status = "canceled"
        else:
            status = "open"
        return {
            "qty": qty,
            "fees": fees,
            "deal_count": len(deals),
            "status": status,
            "effective_order_id": active_order,
            "target_qty": target_qty,
            "remaining_qty": max(target_qty - qty, Decimal("0")),
            "orders": orders,
            "deals": deals,
            "position": {"qty": qty},
        }


class SafetyFixture:
    def __init__(self, *, broker: FakeBroker | None = None, risk_limit: str = "100") -> None:
        self.clock_hours = 0
        self.broker = broker or FakeBroker()
        self.risk_limit = Decimal(risk_limit)
        self.intents: dict[str, Intent] = {}
        self.idem_index: dict[str, str] = {}
        self.reservations: dict[str, Decimal] = {}
        self.memberships: dict[tuple[str, str], bool] = {}
        self.account_bindings: dict[tuple[str, str], AccountBinding] = {}
        self.owner_epochs: dict[str, int] = {}
        self.owner_leases: dict[tuple[str, int], int] = {}
        self.resources: dict[str, dict[str, Any]] = {}
        self.cache: dict[tuple[str, str, str], Any] = {}
        self.jobs: dict[str, dict[str, Any]] = {}
        self.provider_calls = 0
        self.artifacts: dict[str, bytes] = {}
        self.published: dict[str, dict[str, Any]] = {}
        self.datasets: dict[str, list[dict[str, Any]]] = {}
        self.run_manifests: dict[str, dict[str, Any]] = {}
        self.write_lanes_enabled = True
        self.risk_trace: list[tuple[str, str]] = []
        self._lock = threading.RLock()

    def tick(self, hours: int) -> None:
        self.clock_hours += hours

    def grant(self, principal: str, workspace_id: str) -> None:
        self.memberships[(principal, workspace_id)] = True

    def revoke(self, principal: str, workspace_id: str) -> None:
        self.memberships[(principal, workspace_id)] = False

    def bind_account(self, workspace_id: str, account: str, binding: AccountBinding) -> None:
        self.account_bindings[(workspace_id, account)] = binding

    def _authorized(self, principal: str, workspace_id: str) -> bool:
        return self.memberships.get((principal, workspace_id), False)

    def _authorize_resource(self, principal: str, workspace_id: str, resource_id: str) -> dict[str, Any]:
        if not self._authorized(principal, workspace_id):
            raise SafetyError("NOT_FOUND_OR_FORBIDDEN")
        item = self.resources.get(resource_id)
        if item is None or item["workspace_id"] != workspace_id:
            raise SafetyError("NOT_FOUND_OR_FORBIDDEN")
        return item

    def _current_owner_epoch(self, account: str) -> int:
        epoch = self.owner_epochs.get(account)
        if epoch is None:
            raise SafetyError("OWNER_FENCE_DENIED", "no_current_owner")
        return epoch

    def _broker_send(self, record: Intent, owner_epoch: int, outcome: str) -> str:
        if not self.owner_can_send(record.binding.account, owner_epoch):
            raise SafetyError("OWNER_FENCE_DENIED", "stale_epoch_or_expired_lease")
        record.owner_epoch = owner_epoch
        assert record.dispatch_token is not None
        return self.broker.send(record.dispatch_token, outcome)

    def _scope_conflict(self, record: Intent, request: dict[str, Any], payload_hash: str) -> bool:
        return any(
            (
                record.workspace_id != request["workspace_id"],
                record.binding != request["binding"],
                record.contract_version != request.get("contract_version", "F1-C2"),
                record.payload_hash != payload_hash,
            )
        )

    def _existing_idempotent(self, request: dict[str, Any], payload_hash: str) -> dict[str, Any] | None:
        intent_id = self.idem_index.get(request["idempotency_key"])
        if intent_id is None:
            return None
        record = self.intents[intent_id]
        if self._scope_conflict(record, request, payload_hash):
            raise SafetyError("IDEMPOTENCY_CONFLICT", "scope_or_payload_mismatch")
        if record.state in {"unknown", "reconciling", "dispatching"}:
            return self._intent_view(record)
        if record.valid_until is not None and self.clock_hours > record.valid_until:
            raise SafetyError("IDEMPOTENCY_EXPIRED", "new_work_requires_new_key")
        return self._intent_view(record)

    def _intent_view(self, record: Intent) -> dict[str, Any]:
        return {
            "intent_id": record.intent_id,
            "state": record.state,
            "outcome": record.outcome,
            "revision": record.revision,
            "dispatch_token": record.dispatch_token,
        }

    def _reserve(self, record: Intent) -> bool:
        current = sum(self.reservations.values(), Decimal("0"))
        if current + record.risk > self.risk_limit:
            record.state = "rejected"
            record.outcome = "risk_rejected"
            record.terminal_at = self.clock_hours
            record.valid_until = self.clock_hours + IDEMPOTENCY_HOURS
            record.revision += 1
            return False
        self.reservations[record.intent_id] = record.risk
        record.state = "reserved"
        record.revision += 1
        return True

    def submit_intent(
        self,
        request: dict[str, Any],
        *,
        failpoint: str | None = None,
        broker_outcome: str = "accepted",
    ) -> dict[str, Any]:
        with self._lock:
            if failpoint == "C-EXE-03A":
                raise InjectedCrash(failpoint)
            if not self.write_lanes_enabled:
                raise SafetyError("WRITE_LANE_GATED")
            if not self._authorized(request["principal"], request["workspace_id"]):
                raise SafetyError("AUTH_DENIED")
            payload_hash = canonical_hash(request["payload"])
            existing = self._existing_idempotent(request, payload_hash)
            if existing is not None:
                return existing
            bound = self.account_bindings.get((request["workspace_id"], request["binding"].account))
            if bound != request["binding"]:
                raise SafetyError("ACCOUNT_BINDING_STALE")
            if int(request.get("quote_age", 0)) > int(request.get("max_quote_age", 5)):
                raise SafetyError("FRESHNESS_STALE")

            intent_id = f"intent-{len(self.intents) + 1:04d}"
            record = Intent(
                intent_id=intent_id,
                workspace_id=request["workspace_id"],
                key=request["idempotency_key"],
                payload_hash=payload_hash,
                binding=request["binding"],
                contract_version=request.get("contract_version", "F1-C2"),
                risk=Decimal(str(request["risk"])),
                owner_epoch=int(request["owner_epoch"]),
                state="validated",
            )
            self.intents[intent_id] = record
            self.idem_index[record.key] = intent_id
            if not self._reserve(record):
                return self._intent_view(record)
            if failpoint == "C-EXE-03B":
                raise InjectedCrash(failpoint)

            record.dispatch_token = f"dispatch-{intent_id}"
            record.state = "dispatching"
            record.revision += 1
            if failpoint == "C-EXE-03C":
                raise InjectedCrash(failpoint)

            outcome = self._broker_send(record, int(request["owner_epoch"]), broker_outcome)
            if failpoint == "C-EXE-04A":
                raise InjectedCrash(failpoint)

            record.outcome = outcome
            record.state = outcome if outcome in {"accepted", "rejected"} else "unknown"
            record.revision += 1
            if record.state in {"accepted", "rejected"}:
                record.terminal_at = self.clock_hours
                record.valid_until = self.clock_hours + IDEMPOTENCY_HOURS
            if failpoint == "C-EXE-04B":
                raise InjectedCrash(failpoint)
            return self._intent_view(record)

    def recover(
        self,
        intent_id: str,
        *,
        principal: str,
        owner_epoch: int | None = None,
        broker_outcome: str = "accepted",
    ) -> dict[str, Any]:
        with self._lock:
            record = self.intents[intent_id]
            if not self._authorized(principal, record.workspace_id):
                raise SafetyError("AUTH_DENIED")
            current_binding = self.account_bindings.get((record.workspace_id, record.binding.account))
            if current_binding != record.binding:
                raise SafetyError("ACCOUNT_BINDING_STALE")
            send_epoch = self._current_owner_epoch(record.binding.account) if owner_epoch is None else owner_epoch

            if record.state == "reserved":
                record.dispatch_token = f"dispatch-{record.intent_id}"
                record.state = "dispatching"
                record.revision += 1
                record.recovery_log.append("resume_after_reservation")

            if record.state == "dispatching":
                assert record.dispatch_token is not None
                evidence = self.broker.query(record.dispatch_token)
                record.recovery_log.append(f"query:{evidence}")
                if evidence == "absent":
                    outcome = self._broker_send(record, send_epoch, broker_outcome)
                    record.recovery_log.append("send_after_proven_absence")
                    record.outcome = outcome
                    record.state = outcome if outcome in {"accepted", "rejected"} else "unknown"
                elif evidence in {"accepted", "rejected"}:
                    record.state = "unknown"
                    record.recovery_log.append("unknown_after_possible_send")
                    record.state = "reconciling"
                    record.recovery_log.append("reconciling")
                    record.outcome = evidence
                    record.state = evidence
                else:
                    record.state = "unknown"
                    record.recovery_log.append("unknown_unprovable_absence")
                record.revision += 1

            if record.state in {"accepted", "rejected"} and record.terminal_at is None:
                record.terminal_at = self.clock_hours
                record.valid_until = self.clock_hours + IDEMPOTENCY_HOURS
            return self._intent_view(record)

    def reserve_only(
        self,
        intent_id: str,
        amount: Decimal,
        *,
        stage_hook: Callable[[str, str], None] | None = None,
    ) -> bool:
        with self._lock:
            self.risk_trace.append((intent_id, "read"))
            if stage_hook is not None:
                stage_hook(intent_id, "read")
            current = sum(self.reservations.values(), Decimal("0"))
            self.risk_trace.append((intent_id, "check"))
            if stage_hook is not None:
                stage_hook(intent_id, "check")
            if current + amount > self.risk_limit:
                self.risk_trace.append((intent_id, "reject"))
                return False
            self.reservations[intent_id] = amount
            self.risk_trace.append((intent_id, "write"))
            if stage_hook is not None:
                stage_hook(intent_id, "write")
            return True

    def claim_owner(self, account: str, *, lease_hours: int = 1) -> tuple[str, int]:
        epoch = self.owner_epochs.get(account, 0) + 1
        self.owner_epochs[account] = epoch
        self.owner_leases[(account, epoch)] = self.clock_hours + lease_hours
        return account, epoch

    def owner_can_send(self, account: str, epoch: int) -> bool:
        return self.owner_epochs.get(account) == epoch and self.owner_leases.get((account, epoch), -1) >= self.clock_hours

    def reconcile_events(
        self,
        events: Iterable[dict[str, Any]],
        order_qty: Decimal,
        *,
        root_order_id: str = "o1",
    ) -> dict[str, Any]:
        # Implementation deliberately differs structurally from IndependentOracle.
        materialized = [copy.deepcopy(event) for event in events]
        grouped: dict[str, list[dict[str, Any]]] = {}
        for event in materialized:
            if event["kind"] in {"fill", "correction"}:
                grouped.setdefault(event["deal_id"], []).append(event)
        effective = [max(group, key=lambda event: int(event["version"])) for group in grouped.values()]
        deals = [
            {
                "deal_id": event["deal_id"],
                "order_id": event["order_id"],
                "version": int(event["version"]),
                "qty": Decimal(str(event["qty"])),
                "fee": Decimal(str(event["fee"])),
            }
            for event in sorted(effective, key=lambda event: event["deal_id"])
        ]

        orders: dict[str, dict[str, Any]] = {
            root_order_id: {"status": "open", "target_qty": order_qty, "replaced_by": None}
        }
        active_order = root_order_id
        for event in sorted(
            (event for event in materialized if event["kind"] in {"replace", "cancel"}),
            key=lambda event: int(event["seq"]),
        ):
            if event["kind"] == "replace":
                new_qty = Decimal(str(event["new_qty"]))
                if event["order_id"] != active_order or new_qty <= 0:
                    raise SafetyError("RECONCILE_INVALID_REPLACE")
                orders[active_order]["status"] = "replaced"
                orders[active_order]["replaced_by"] = event["new_order_id"]
                active_order = event["new_order_id"]
                orders[active_order] = {"status": "open", "target_qty": new_qty, "replaced_by": None}
            elif event["order_id"] in orders:
                orders[event["order_id"]]["status"] = "canceled"

        qty = sum((deal["qty"] for deal in deals), Decimal("0"))
        fees = sum((deal["fee"] for deal in deals), Decimal("0"))
        target_qty = Decimal(str(orders[active_order]["target_qty"]))
        canceled = orders[active_order]["status"] == "canceled"
        status = "filled" if qty >= target_qty else "partially_filled" if qty > 0 else "open"
        if canceled and qty < target_qty:
            status = "partially_filled_canceled" if qty > 0 else "canceled"
        return {
            "qty": qty,
            "fees": fees,
            "deal_count": len(deals),
            "status": status,
            "effective_order_id": active_order,
            "target_qty": target_qty,
            "remaining_qty": max(target_qty - qty, Decimal("0")),
            "orders": orders,
            "deals": deals,
            "position": {"qty": qty},
        }

    # Tenant-scoped read/cache/export/realtime/job/AI seams.
    def add_resource(self, resource_id: str, workspace_id: str, payload: Any) -> None:
        self.resources[resource_id] = {"workspace_id": workspace_id, "payload": payload}

    def protected_read(self, principal: str, workspace_id: str, resource_id: str) -> Any:
        item = self._authorize_resource(principal, workspace_id, resource_id)
        return copy.deepcopy(item["payload"])

    def cached_read(self, principal: str, workspace_id: str, resource_id: str) -> Any:
        self._authorize_resource(principal, workspace_id, resource_id)
        key = (principal, workspace_id, resource_id)
        if key not in self.cache:
            self.cache[key] = self.protected_read(principal, workspace_id, resource_id)
        return copy.deepcopy(self.cache[key])

    def export_resource(self, principal: str, workspace_id: str, resource_id: str) -> bytes:
        return json.dumps(self.protected_read(principal, workspace_id, resource_id), sort_keys=True).encode("utf-8")

    def realtime_subscribe(self, principal: str, workspace_id: str, resource_id: str) -> str:
        self.protected_read(principal, workspace_id, resource_id)
        return f"channel:{workspace_id}:{resource_id}"

    def enqueue_job(self, job_id: str, principal: str, workspace_id: str, resource_id: str) -> None:
        self.protected_read(principal, workspace_id, resource_id)
        if job_id in self.jobs:
            raise SafetyError("JOB_ID_CONFLICT")
        self.jobs[job_id] = {
            "principal": principal,
            "workspace_id": workspace_id,
            "resource_id": resource_id,
            "state": "queued",
        }

    def dispatch_job(self, job_id: str) -> dict[str, Any]:
        job = self.jobs[job_id]
        if not self._authorized(job["principal"], job["workspace_id"]):
            job["state"] = "denied"
            raise SafetyError("AUTH_DENIED")
        payload = self.protected_read(job["principal"], job["workspace_id"], job["resource_id"])
        job["state"] = "running"
        return {"workspace_id": job["workspace_id"], "payload": payload}

    def ai_context(
        self,
        principal: str,
        workspace_id: str,
        resource_ids: list[str],
        fields: dict[str, Any],
    ) -> dict[str, Any]:
        forbidden = {"credential", "token", "holdout_body", "broker_action"}
        if forbidden.intersection(fields):
            raise SafetyError("AI_CONTEXT_FORBIDDEN")
        context = [self.protected_read(principal, workspace_id, rid) for rid in resource_ids]
        self.provider_calls += 1
        return {"workspace_id": workspace_id, "context": context, "fields": copy.deepcopy(fields)}

    @staticmethod
    def redact_log(record: dict[str, Any]) -> dict[str, Any]:
        protected = {"secret", "token", "holdout_body", "credential"}
        return {key: ("[REDACTED]" if key in protected else value) for key, value in record.items()}

    # Artifact/data/restore seams.
    def stage_artifact(self, artifact_id: str, body: bytes) -> str:
        digest = hashlib.sha256(body).hexdigest()
        self.artifacts[f"staged:{artifact_id}:{digest}"] = body
        return digest

    def publish_artifact(self, artifact_id: str, digest: str, receipt_digest: str) -> None:
        if digest != receipt_digest:
            raise SafetyError("VERIFICATION_HASH_MISMATCH")
        staged_key = f"staged:{artifact_id}:{digest}"
        body = self.artifacts.get(staged_key)
        if body is None or hashlib.sha256(body).hexdigest() != digest:
            raise SafetyError("STAGED_ARTIFACT_MISSING_OR_CHANGED")
        self.published[artifact_id] = {"sha256": digest, "size": len(body)}

    def create_dataset(self, dataset_id: str, rows: list[dict[str, Any]], *, parent_hash: str | None = None) -> dict[str, Any]:
        version = {
            "dataset_id": dataset_id,
            "version": len(self.datasets.get(dataset_id, [])) + 1,
            "rows": copy.deepcopy(rows),
            "sha256": canonical_hash(rows),
            "parent_hash": parent_hash,
        }
        self.datasets.setdefault(dataset_id, []).append(version)
        return copy.deepcopy(version)

    @staticmethod
    def guarded_rows(version: dict[str, Any], *, cutoff_known_at: int) -> list[dict[str, Any]]:
        rows = []
        for row in version["rows"]:
            if row.get("classification") == "holdout" or int(row["known_at"]) > cutoff_known_at:
                raise SafetyError("FUTURE_OR_HOLDOUT_GUARD")
            rows.append(copy.deepcopy(row))
        return rows

    def record_run(self, run_id: str, dataset: dict[str, Any], cutoff_known_at: int) -> None:
        manifest = {
            "run_id": run_id,
            "dataset_id": dataset["dataset_id"],
            "dataset_version": dataset["version"],
            "dataset_sha256": dataset["sha256"],
            "cutoff_known_at": cutoff_known_at,
        }
        manifest["manifest_sha256"] = canonical_hash(manifest)
        self.run_manifests[run_id] = manifest

    @staticmethod
    def _build_restore_proof(metadata: dict[str, Any], artifacts: dict[str, bytes]) -> dict[str, Any]:
        artifact_hashes = {key: hashlib.sha256(value).hexdigest() for key, value in sorted(artifacts.items())}
        dataset_versions = {
            dataset_id: [
                {
                    "version": version["version"],
                    "rows_sha256": canonical_hash(version["rows"]),
                    "declared_sha256": version["sha256"],
                    "parent_hash": version["parent_hash"],
                }
                for version in versions
            ]
            for dataset_id, versions in sorted(metadata["datasets"].items())
        }
        return {
            "metadata_sha256": canonical_hash(metadata),
            "intent_ids": sorted(metadata["intents"]),
            "published_ids": sorted(metadata["published"]),
            "dataset_ids": sorted(metadata["datasets"]),
            "dataset_versions": dataset_versions,
            "run_manifest_hashes": {
                run_id: canonical_hash(manifest) for run_id, manifest in sorted(metadata["run_manifests"].items())
            },
            "artifact_hashes": artifact_hashes,
            "counts": {
                "intents": len(metadata["intents"]),
                "published": len(metadata["published"]),
                "datasets": len(metadata["datasets"]),
                "runs": len(metadata["run_manifests"]),
                "artifacts": len(artifacts),
            },
        }

    @staticmethod
    def _validate_restore_integrity(metadata: dict[str, Any], artifacts: dict[str, bytes]) -> None:
        for key, intent_id in metadata["idem_index"].items():
            record = metadata["intents"].get(intent_id)
            if record is None or record.key != key:
                raise SafetyError("RESTORE_METADATA_INVALID", "idempotency_reference")
        for intent_id, amount in metadata["reservations"].items():
            record = metadata["intents"].get(intent_id)
            if record is None or Decimal(str(amount)) != record.risk:
                raise SafetyError("RESTORE_METADATA_INVALID", "reservation_reference")

        for dataset_id, versions in metadata["datasets"].items():
            previous_hash: str | None = None
            for index, version in enumerate(versions, start=1):
                if version["dataset_id"] != dataset_id or int(version["version"]) != index:
                    raise SafetyError("RESTORE_METADATA_INVALID", "dataset_identity")
                actual_rows_hash = canonical_hash(version["rows"])
                if version["sha256"] != actual_rows_hash:
                    raise SafetyError("RESTORE_DATASET_HASH_MISMATCH")
                if index == 1:
                    if version["parent_hash"] is not None:
                        raise SafetyError("RESTORE_LINEAGE_MISMATCH", "unexpected_root_parent")
                elif version["parent_hash"] != previous_hash:
                    raise SafetyError("RESTORE_LINEAGE_MISMATCH", "parent_hash")
                previous_hash = actual_rows_hash

        for run_id, manifest in metadata["run_manifests"].items():
            unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
            if manifest.get("run_id") != run_id or manifest.get("manifest_sha256") != canonical_hash(unsigned):
                raise SafetyError("RESTORE_RUN_HASH_MISMATCH")
            versions = metadata["datasets"].get(manifest["dataset_id"], [])
            version_number = int(manifest["dataset_version"])
            if version_number < 1 or version_number > len(versions):
                raise SafetyError("RESTORE_RUN_REFERENCE_MISMATCH", "dataset_version")
            referenced = versions[version_number - 1]
            if referenced["sha256"] != manifest["dataset_sha256"]:
                raise SafetyError("RESTORE_RUN_REFERENCE_MISMATCH", "dataset_sha256")

        for artifact_id, published in metadata["published"].items():
            digest = published["sha256"]
            body = artifacts.get(f"staged:{artifact_id}:{digest}")
            if body is None or hashlib.sha256(body).hexdigest() != digest or len(body) != int(published["size"]):
                raise SafetyError("RESTORE_ARTIFACT_HASH_MISMATCH")

    def backup(self) -> dict[str, Any]:
        metadata = {
            "intents": copy.deepcopy(self.intents),
            "idem_index": copy.deepcopy(self.idem_index),
            "reservations": copy.deepcopy(self.reservations),
            "published": copy.deepcopy(self.published),
            "datasets": copy.deepcopy(self.datasets),
            "run_manifests": copy.deepcopy(self.run_manifests),
        }
        self._validate_restore_integrity(metadata, self.artifacts)
        proof = self._build_restore_proof(metadata, self.artifacts)
        return {"metadata": metadata, "artifacts": copy.deepcopy(self.artifacts), "proof": proof}

    def restore(self, backup: dict[str, Any]) -> dict[str, Any]:
        self.write_lanes_enabled = False
        try:
            metadata = copy.deepcopy(backup["metadata"])
            artifacts = copy.deepcopy(backup["artifacts"])
            self._validate_restore_integrity(metadata, artifacts)
            proof = self._build_restore_proof(metadata, artifacts)
            if proof != backup["proof"]:
                raise SafetyError("RESTORE_PROOF_MISMATCH")
        except SafetyError:
            raise
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise SafetyError("RESTORE_METADATA_INVALID", type(exc).__name__) from exc

        self.intents = metadata["intents"]
        self.idem_index = metadata["idem_index"]
        self.reservations = metadata["reservations"]
        self.published = metadata["published"]
        self.datasets = metadata["datasets"]
        self.run_manifests = metadata["run_manifests"]
        self.artifacts = artifacts
        outstanding = [i for i in self.intents.values() if i.state in {"dispatching", "unknown", "reconciling"}]
        self.write_lanes_enabled = not outstanding
        return proof

    def reconcile_restored_intents(self, principal: str) -> None:
        for intent in list(self.intents.values()):
            if intent.state in {"dispatching", "unknown", "reconciling"}:
                if intent.state != "dispatching":
                    intent.state = "dispatching"
                self.recover(
                    intent.intent_id,
                    principal=principal,
                    owner_epoch=self._current_owner_epoch(intent.binding.account),
                )
        self.write_lanes_enabled = not any(
            i.state in {"dispatching", "unknown", "reconciling"} for i in self.intents.values()
        )
