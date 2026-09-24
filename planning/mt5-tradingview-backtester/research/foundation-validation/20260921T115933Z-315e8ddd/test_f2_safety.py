from __future__ import annotations

import itertools
import random
import threading
import unittest
from copy import deepcopy
from decimal import Decimal

from f2_safety_fixture import (
    IDEMPOTENCY_HOURS,
    SEEDS,
    AccountBinding,
    FakeBroker,
    IndependentOracle,
    InjectedCrash,
    SafetyError,
    SafetyFixture,
    canonical_hash,
)


def request(
    key: str = "idem-1",
    *,
    payload_qty: str = "1",
    risk: str = "30",
    owner_epoch: int = 1,
) -> dict:
    binding = AccountBinding("fake", "sandbox", "A-001", "paper")
    return {
        "principal": "alice",
        "workspace_id": "tenant-a",
        "idempotency_key": key,
        "binding": binding,
        "contract_version": "F1-C2",
        "payload": {"symbol": "SYNTH", "side": "buy", "qty": payload_qty},
        "risk": risk,
        "owner_epoch": owner_epoch,
        "quote_age": 1,
        "max_quote_age": 5,
    }


def configured(*, broker: FakeBroker | None = None, risk_limit: str = "100") -> SafetyFixture:
    fx = SafetyFixture(broker=broker, risk_limit=risk_limit)
    fx.grant("alice", "tenant-a")
    fx.grant("bob", "tenant-b")
    fx.bind_account("tenant-a", "A-001", AccountBinding("fake", "sandbox", "A-001", "paper"))
    fx.claim_owner("A-001", lease_hours=1)
    return fx


class Safe01IdempotencyTests(unittest.TestCase):
    def test_same_intent_retries_and_conflicting_payload_or_scope(self) -> None:
        # C-EXE-01/02, C-ID-05, E-SAFE-01.
        for seed in SEEDS:
            rnd = random.Random(seed)
            fx = configured()
            calls = [request(), request()]
            rnd.shuffle(calls)
            results = [fx.submit_intent(item) for item in calls]
            self.assertEqual(results[0]["intent_id"], results[1]["intent_id"])
            self.assertEqual(fx.broker.send_count(), 1)

            with self.assertRaisesRegex(SafetyError, "IDEMPOTENCY_CONFLICT"):
                fx.submit_intent(request(payload_qty="2"))
            self.assertEqual(fx.broker.send_count(), 1)

            foreign = request()
            foreign["workspace_id"] = "tenant-b"
            foreign["principal"] = "bob"
            with self.assertRaisesRegex(SafetyError, "IDEMPOTENCY_CONFLICT"):
                fx.submit_intent(foreign)
            self.assertEqual(fx.broker.send_count(), 1)

    def test_same_intent_threaded_retries_one_send_across_seeds(self) -> None:
        # E-SAFE-01: two live threads cross the same start barrier for each seed.
        for seed in SEEDS:
            fx = configured()
            barrier = threading.Barrier(3)
            results: list[dict] = []
            errors: list[BaseException] = []
            result_lock = threading.Lock()

            def worker() -> None:
                try:
                    barrier.wait()
                    result = fx.submit_intent(request())
                    with result_lock:
                        results.append(result)
                except BaseException as exc:  # captured so thread failures fail the test deterministically
                    with result_lock:
                        errors.append(exc)

            threads = [threading.Thread(target=worker, name=f"retry-{seed}-{index}") for index in range(2)]
            random.Random(seed).shuffle(threads)
            for thread in threads:
                thread.start()
            barrier.wait()
            for thread in threads:
                thread.join()

            self.assertEqual(errors, [])
            self.assertEqual(len(results), 2)
            self.assertEqual({result["intent_id"] for result in results}, {"intent-0001"})
            self.assertEqual(fx.broker.send_count(), 1)

    def test_f1_c2_idempotency_retention_expiry_and_unknown_nonexpiry(self) -> None:
        # C-IDEM-01/02/03.
        fx = configured()
        first = fx.submit_intent(request())
        fx.tick(IDEMPOTENCY_HOURS)
        replay = fx.submit_intent(request())
        self.assertEqual(replay, first)
        self.assertEqual(fx.broker.send_count(), 1)
        fx.tick(1)
        with self.assertRaisesRegex(SafetyError, "IDEMPOTENCY_EXPIRED"):
            fx.submit_intent(request())
        self.assertEqual(fx.broker.send_count(), 1)

        fx2 = configured(broker=FakeBroker(can_prove_absence=False))
        with self.assertRaises(InjectedCrash):
            fx2.submit_intent(request(), failpoint="C-EXE-03C")
        fx2.recover("intent-0001", principal="alice")
        self.assertEqual(fx2.intents["intent-0001"].state, "unknown")
        fx2.tick(IDEMPOTENCY_HOURS + 24)
        replay_unknown = fx2.submit_intent(request())
        self.assertEqual(replay_unknown["state"], "unknown")
        self.assertEqual(fx2.broker.send_count(), 0)


class Safe02CrashWindowTests(unittest.TestCase):
    def test_c_exe_03a_before_durable_receive(self) -> None:
        fx = configured()
        with self.assertRaises(InjectedCrash):
            fx.submit_intent(request(), failpoint="C-EXE-03A")
        self.assertEqual(fx.intents, {})
        self.assertEqual(fx.broker.send_count(), 0)
        self.assertEqual(fx.submit_intent(request())["state"], "accepted")
        self.assertEqual(fx.broker.send_count(), 1)

    def test_c_exe_03b_after_reservation_before_dispatch(self) -> None:
        fx = configured()
        with self.assertRaises(InjectedCrash):
            fx.submit_intent(request(), failpoint="C-EXE-03B")
        self.assertEqual(fx.intents["intent-0001"].state, "reserved")
        self.assertEqual(fx.broker.send_count(), 0)
        recovered = fx.recover("intent-0001", principal="alice")
        self.assertEqual(recovered["state"], "accepted")
        self.assertEqual(fx.broker.send_count(), 1)

    def test_c_exe_03c_query_first_and_never_blind_resend(self) -> None:
        for can_prove_absence in (True, False):
            fx = configured(broker=FakeBroker(can_prove_absence=can_prove_absence))
            with self.assertRaises(InjectedCrash):
                fx.submit_intent(request(), failpoint="C-EXE-03C")
            self.assertEqual(fx.broker.send_count(), 0)
            recovered = fx.recover("intent-0001", principal="alice")
            if can_prove_absence:
                self.assertEqual(recovered["state"], "accepted")
                self.assertEqual(fx.broker.send_count(), 1)
            else:
                self.assertEqual(recovered["state"], "unknown")
                self.assertEqual(fx.broker.send_count(), 0)
                self.assertIn("unknown_unprovable_absence", fx.intents["intent-0001"].recovery_log)

    def test_c_exe_04a_possible_send_reconciles_without_resend(self) -> None:
        fx = configured()
        with self.assertRaises(InjectedCrash):
            fx.submit_intent(request(), failpoint="C-EXE-04A")
        self.assertEqual(fx.broker.send_count(), 1)
        recovered = fx.recover("intent-0001", principal="alice")
        self.assertEqual(recovered["state"], "accepted")
        self.assertEqual(fx.broker.send_count(), 1)
        self.assertIn("unknown_after_possible_send", fx.intents["intent-0001"].recovery_log)
        self.assertIn("reconciling", fx.intents["intent-0001"].recovery_log)

    def test_c_exe_04b_durable_outcome_retry_returns_stored(self) -> None:
        fx = configured()
        with self.assertRaises(InjectedCrash):
            fx.submit_intent(request(), failpoint="C-EXE-04B")
        self.assertEqual(fx.broker.send_count(), 1)
        replay = fx.submit_intent(request())
        self.assertEqual(replay["state"], "accepted")
        self.assertEqual(fx.broker.send_count(), 1)


class Safe03RiskTests(unittest.TestCase):
    def test_atomic_risk_reservation_matches_independent_oracle_across_orders(self) -> None:
        # E-SAFE-03/C-EXE-05. 24 complete interleavings plus seeded shuffles.
        items = [("i1", Decimal("55")), ("i2", Decimal("50")), ("i3", Decimal("30")), ("i4", Decimal("20"))]
        orders = list(itertools.permutations(items))
        for seed in SEEDS:
            seeded = list(items)
            random.Random(seed).shuffle(seeded)
            orders.append(tuple(seeded))
        for order in orders:
            fx = configured(risk_limit="100")
            actual = [intent_id for intent_id, amount in order if fx.reserve_only(intent_id, amount)]
            expected, expected_sum = IndependentOracle.risk_acceptance(order, Decimal("100"))
            self.assertEqual(actual, expected)
            self.assertEqual(sum(fx.reservations.values(), Decimal("0")), expected_sum)
            self.assertLessEqual(expected_sum, Decimal("100"))

    def test_threaded_risk_read_check_write_is_atomic_across_seeds(self) -> None:
        # E-SAFE-03: all contenders start concurrently; trace proves read/check/write stays atomic.
        items = [("i1", Decimal("55")), ("i2", Decimal("50")), ("i3", Decimal("30")), ("i4", Decimal("20"))]
        for seed in SEEDS:
            fx = configured(risk_limit="100")
            barrier = threading.Barrier(len(items) + 1)
            errors: list[BaseException] = []
            error_lock = threading.Lock()

            def worker(intent_id: str, amount: Decimal) -> None:
                try:
                    barrier.wait()
                    fx.reserve_only(intent_id, amount)
                except BaseException as exc:
                    with error_lock:
                        errors.append(exc)

            shuffled = list(items)
            random.Random(seed).shuffle(shuffled)
            threads = [threading.Thread(target=worker, args=item, name=f"risk-{seed}-{item[0]}") for item in shuffled]
            for thread in threads:
                thread.start()
            barrier.wait()
            for thread in threads:
                thread.join()

            self.assertEqual(errors, [])
            observed_order = [intent_id for intent_id, stage in fx.risk_trace if stage == "read"]
            amount_by_id = dict(items)
            expected, expected_sum = IndependentOracle.risk_acceptance(
                [(intent_id, amount_by_id[intent_id]) for intent_id in observed_order],
                Decimal("100"),
            )
            self.assertEqual(list(fx.reservations), expected)
            self.assertEqual(sum(fx.reservations.values(), Decimal("0")), expected_sum)
            self.assertLessEqual(expected_sum, Decimal("100"))
            self.assertEqual(len(fx.risk_trace), len(items) * 3)
            for offset in range(0, len(fx.risk_trace), 3):
                chunk = fx.risk_trace[offset : offset + 3]
                self.assertEqual({entry[0] for entry in chunk}, {chunk[0][0]})
                self.assertEqual([entry[1] for entry in chunk[:2]], ["read", "check"])
                self.assertIn(chunk[2][1], {"write", "reject"})


class Safe04FencingTests(unittest.TestCase):
    def test_stale_owner_partition_and_expired_lease_fail_closed(self) -> None:
        # E-SAFE-04: stale authority is rejected in the path immediately before FakeBroker.send.
        stale = configured()
        self.assertTrue(stale.owner_can_send("A-001", 1))
        _, epoch2 = stale.claim_owner("A-001")
        self.assertFalse(stale.owner_can_send("A-001", 1))
        self.assertTrue(stale.owner_can_send("A-001", epoch2))
        with self.assertRaisesRegex(SafetyError, "OWNER_FENCE_DENIED"):
            stale.submit_intent(request(key="stale-owner", owner_epoch=1))
        self.assertEqual(stale.broker.send_count(), 0)

        expired = configured()
        expired.tick(2)
        self.assertFalse(expired.owner_can_send("A-001", 1))
        with self.assertRaisesRegex(SafetyError, "OWNER_FENCE_DENIED"):
            expired.submit_intent(request(key="expired-owner", owner_epoch=1))
        self.assertEqual(expired.broker.send_count(), 0)

        current = configured()
        self.assertEqual(current.submit_intent(request(key="current-owner"))["state"], "accepted")
        self.assertEqual(current.broker.send_count(), 1)

    def test_expired_intent_key_and_account_switch_or_stale_quote_cannot_send(self) -> None:
        fx = configured()
        fx.submit_intent(request())
        fx.tick(IDEMPOTENCY_HOURS + 1)
        with self.assertRaisesRegex(SafetyError, "IDEMPOTENCY_EXPIRED"):
            fx.submit_intent(request())
        self.assertEqual(fx.broker.send_count(), 1)

        switched = configured()
        switched.bind_account("tenant-a", "A-001", AccountBinding("fake", "other", "A-001", "paper"))
        with self.assertRaisesRegex(SafetyError, "ACCOUNT_BINDING_STALE"):
            switched.submit_intent(request(key="switch"))
        stale = configured()
        stale_req = request(key="stale")
        stale_req["quote_age"] = 99
        with self.assertRaisesRegex(SafetyError, "FRESHNESS_STALE"):
            stale.submit_intent(stale_req)
        self.assertEqual(switched.broker.send_count() + stale.broker.send_count(), 0)


class Safe05ReconcileTests(unittest.TestCase):
    def test_partial_duplicate_reordered_correction_cancel_replace_matches_oracle(self) -> None:
        # E-SAFE-05/C-EXE-07. Reconcile order/deal/position state, not event count.
        events = [
            {"kind": "fill", "seq": 10, "order_id": "o1", "deal_id": "d1", "version": 1, "qty": "40", "fee": "0.40"},
            {"kind": "fill", "seq": 10, "order_id": "o1", "deal_id": "d1", "version": 1, "qty": "40", "fee": "0.40"},
            {"kind": "replace", "seq": 20, "order_id": "o1", "new_order_id": "o2", "new_qty": "80"},
            {"kind": "fill", "seq": 30, "order_id": "o2", "deal_id": "d2", "version": 1, "qty": "20", "fee": "0.20"},
            {"kind": "correction", "seq": 40, "order_id": "o2", "deal_id": "d2", "version": 2, "qty": "15", "fee": "0.15", "correction_of": "d2:v1"},
            {"kind": "cancel", "seq": 50, "order_id": "o2"},
        ]
        for seed in SEEDS:
            shuffled = list(events)
            random.Random(seed).shuffle(shuffled)
            actual = configured().reconcile_events(shuffled, Decimal("100"))
            expected = IndependentOracle.reconcile(shuffled, Decimal("100"))
            self.assertEqual(actual, expected)
            self.assertEqual(actual["qty"], Decimal("55"))
            self.assertEqual(actual["fees"], Decimal("0.55"))
            self.assertEqual(actual["deal_count"], 2)
            self.assertEqual(actual["status"], "partially_filled_canceled")
            self.assertEqual(actual["effective_order_id"], "o2")
            self.assertEqual(actual["target_qty"], Decimal("80"))
            self.assertEqual(actual["remaining_qty"], Decimal("25"))
            self.assertEqual(actual["orders"]["o1"]["status"], "replaced")
            self.assertEqual(actual["orders"]["o1"]["replaced_by"], "o2")
            self.assertEqual(actual["orders"]["o2"]["status"], "canceled")
            self.assertEqual(actual["position"], {"qty": Decimal("55")})

            without_replace = [event for event in shuffled if event["kind"] != "replace"]
            without_replace = [
                {**event, "order_id": "o1"} if event.get("order_id") == "o2" else event
                for event in without_replace
            ]
            baseline = configured().reconcile_events(without_replace, Decimal("100"))
            self.assertEqual(baseline["effective_order_id"], "o1")
            self.assertEqual(baseline["target_qty"], Decimal("100"))
            self.assertNotEqual(actual["remaining_qty"], baseline["remaining_qty"])

    def test_cancel_then_replace_replays_lifecycle_in_sequence_order(self) -> None:
        events = [
            {"kind": "cancel", "seq": 10, "order_id": "o1"},
            {"kind": "replace", "seq": 20, "order_id": "o1", "new_order_id": "o2", "new_qty": "80"},
        ]
        for seed in SEEDS:
            shuffled = list(events)
            random.Random(seed).shuffle(shuffled)
            actual = configured().reconcile_events(shuffled, Decimal("100"))
            expected = IndependentOracle.reconcile(shuffled, Decimal("100"))
            self.assertEqual(actual, expected)
            self.assertEqual(actual["orders"]["o1"]["status"], "replaced")
            self.assertEqual(actual["effective_order_id"], "o2")
            self.assertEqual(actual["status"], "open")


class TenantIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = configured()
        self.fx.add_resource("ra", "tenant-a", {"value": "A-only"})
        self.fx.add_resource("rb", "tenant-b", {"value": "B-only"})

    def test_api_cache_export_realtime_ai_are_tenant_scoped(self) -> None:
        # E-TENANT-01/C-ID-01/02/C-AI-01.
        self.assertEqual(self.fx.cached_read("alice", "tenant-a", "ra")["value"], "A-only")
        for seam in (
            lambda: self.fx.protected_read("alice", "tenant-a", "rb"),
            lambda: self.fx.cached_read("alice", "tenant-a", "rb"),
            lambda: self.fx.enqueue_job("cross-tenant", "alice", "tenant-a", "rb"),
            lambda: self.fx.export_resource("alice", "tenant-a", "rb"),
            lambda: self.fx.realtime_subscribe("alice", "tenant-a", "rb"),
            lambda: self.fx.protected_read("alice", "tenant-b", "rb"),
            lambda: self.fx.cached_read("alice", "tenant-b", "rb"),
            lambda: self.fx.enqueue_job("spoofed-workspace", "alice", "tenant-b", "rb"),
            lambda: self.fx.export_resource("alice", "tenant-b", "rb"),
            lambda: self.fx.realtime_subscribe("alice", "tenant-b", "rb"),
        ):
            with self.assertRaisesRegex(SafetyError, "NOT_FOUND_OR_FORBIDDEN"):
                seam()
        self.assertNotIn(("alice", "tenant-a", "rb"), self.fx.cache)
        self.assertNotIn(("alice", "tenant-b", "rb"), self.fx.cache)
        with self.assertRaisesRegex(SafetyError, "NOT_FOUND_OR_FORBIDDEN"):
            self.fx.ai_context("alice", "tenant-a", ["rb"], {})
        with self.assertRaisesRegex(SafetyError, "NOT_FOUND_OR_FORBIDDEN"):
            self.fx.ai_context("alice", "tenant-b", ["rb"], {})
        with self.assertRaisesRegex(SafetyError, "AI_CONTEXT_FORBIDDEN"):
            self.fx.ai_context("alice", "tenant-a", ["ra"], {"broker_action": "send"})
        self.assertEqual(self.fx.provider_calls, 0)

        # Cached data is not an authorization bypass after membership changes.
        self.fx.revoke("alice", "tenant-a")
        with self.assertRaisesRegex(SafetyError, "NOT_FOUND_OR_FORBIDDEN"):
            self.fx.cached_read("alice", "tenant-a", "ra")
        self.fx.grant("alice", "tenant-a")

    def test_worker_reuse_role_revoke_and_log_redaction(self) -> None:
        # E-TENANT-02/C-ID-03/04/C-OBS-02.
        self.fx.enqueue_job("ja", "alice", "tenant-a", "ra")
        first = self.fx.dispatch_job("ja")
        self.assertEqual(first, {"workspace_id": "tenant-a", "payload": {"value": "A-only"}})

        self.fx.enqueue_job("jb", "bob", "tenant-b", "rb")
        second = self.fx.dispatch_job("jb")
        self.assertEqual(second, {"workspace_id": "tenant-b", "payload": {"value": "B-only"}})
        self.assertNotIn("A-only", repr(second))

        self.fx.enqueue_job("revoked", "alice", "tenant-a", "ra")
        self.fx.revoke("alice", "tenant-a")
        with self.assertRaisesRegex(SafetyError, "AUTH_DENIED"):
            self.fx.dispatch_job("revoked")
        self.assertEqual(self.fx.jobs["revoked"]["state"], "denied")

        redacted = self.fx.redact_log({"trace_id": "t-1", "secret": "x", "token": "y", "holdout_body": "z"})
        self.assertEqual(redacted["trace_id"], "t-1")
        self.assertEqual({redacted[k] for k in ("secret", "token", "holdout_body")}, {"[REDACTED]"})

    def test_job_id_collision_cannot_overwrite_other_tenant_job(self) -> None:
        self.fx.enqueue_job("shared", "alice", "tenant-a", "ra")
        original = dict(self.fx.jobs["shared"])
        with self.assertRaisesRegex(SafetyError, "JOB_ID_CONFLICT"):
            self.fx.enqueue_job("shared", "bob", "tenant-b", "rb")
        self.assertEqual(self.fx.jobs["shared"], original)
        self.assertEqual(
            self.fx.dispatch_job("shared"),
            {"workspace_id": "tenant-a", "payload": {"value": "A-only"}},
        )


class RestoreTests(unittest.TestCase):
    @staticmethod
    def _source_and_backup() -> tuple[SafetyFixture, dict]:
        source = configured()
        source.add_resource("ra", "tenant-a", {"value": 1})
        digest = source.stage_artifact("result-1", b"deterministic-result")
        source.publish_artifact("result-1", digest, digest)
        v1 = source.create_dataset("ds", [{"event_at": 1, "known_at": 1, "value": 10}])
        v2 = source.create_dataset(
            "ds",
            [{"event_at": 1, "known_at": 1, "value": 11}],
            parent_hash=v1["sha256"],
        )
        source.record_run("run-restore", v2, cutoff_known_at=1)
        try:
            source.submit_intent(request(), failpoint="C-EXE-04A")
        except InjectedCrash:
            pass
        else:
            raise AssertionError("restore fixture expected C-EXE-04A crash")
        return source, source.backup()

    def test_restore_hash_proof_and_reconcile_gate_before_writes(self) -> None:
        # E-RESTORE-01/C-JOB-04 + fresh-environment reconstruction mechanics.
        source, backup = self._source_and_backup()

        restored_broker = FakeBroker()
        restored_broker.evidence.update(source.broker.evidence)
        restored = configured(broker=restored_broker)
        proof = restored.restore(backup)
        self.assertEqual(proof, backup["proof"])
        self.assertEqual(proof["counts"], {"intents": 1, "published": 1, "datasets": 1, "runs": 1, "artifacts": 1})
        self.assertEqual(proof["dataset_versions"]["ds"][1]["parent_hash"], proof["dataset_versions"]["ds"][0]["rows_sha256"])
        self.assertIn("run-restore", proof["run_manifest_hashes"])
        self.assertEqual(len(proof["metadata_sha256"]), 64)
        self.assertFalse(restored.write_lanes_enabled)
        self.assertEqual(restored.broker.send_count(), 0)
        with self.assertRaisesRegex(SafetyError, "WRITE_LANE_GATED"):
            restored.submit_intent(request(key="blocked-before-reconcile"))
        self.assertEqual(restored.broker.send_count(), 0)
        restored.reconcile_restored_intents("alice")
        self.assertTrue(restored.write_lanes_enabled)
        self.assertEqual(restored.intents["intent-0001"].state, "accepted")
        self.assertEqual(restored.broker.send_count(), 0)

    def test_restore_rejects_corrupt_metadata_dataset_lineage_run_and_artifact(self) -> None:
        _, backup = self._source_and_backup()

        corruptions: list[tuple[str, dict, str]] = []

        bad_metadata = deepcopy(backup)
        bad_metadata["metadata"]["intents"]["intent-0001"].workspace_id = "tenant-b"
        corruptions.append(("metadata", bad_metadata, "RESTORE_PROOF_MISMATCH"))

        bad_dataset_hash = deepcopy(backup)
        bad_dataset_hash["metadata"]["datasets"]["ds"][0]["sha256"] = "0" * 64
        corruptions.append(("dataset_hash", bad_dataset_hash, "RESTORE_DATASET_HASH_MISMATCH"))

        bad_lineage = deepcopy(backup)
        bad_lineage["metadata"]["datasets"]["ds"][1]["parent_hash"] = "f" * 64
        corruptions.append(("lineage", bad_lineage, "RESTORE_LINEAGE_MISMATCH"))

        bad_run_hash = deepcopy(backup)
        bad_run_hash["metadata"]["run_manifests"]["run-restore"]["cutoff_known_at"] = 2
        corruptions.append(("run_hash", bad_run_hash, "RESTORE_RUN_HASH_MISMATCH"))

        bad_run_reference = deepcopy(backup)
        manifest = bad_run_reference["metadata"]["run_manifests"]["run-restore"]
        manifest["dataset_sha256"] = "1" * 64
        unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        manifest["manifest_sha256"] = canonical_hash(unsigned)
        corruptions.append(("run_reference", bad_run_reference, "RESTORE_RUN_REFERENCE_MISMATCH"))

        bad_artifact = deepcopy(backup)
        artifact_key = next(iter(bad_artifact["artifacts"]))
        bad_artifact["artifacts"][artifact_key] = b"corrupt-bytes"
        corruptions.append(("artifact", bad_artifact, "RESTORE_ARTIFACT_HASH_MISMATCH"))

        for name, corrupted, expected_code in corruptions:
            with self.subTest(name=name):
                restored = configured()
                with self.assertRaisesRegex(SafetyError, expected_code):
                    restored.restore(corrupted)
                self.assertFalse(restored.write_lanes_enabled)
                self.assertEqual(restored.broker.send_count(), 0)


class DataIntegrityTests(unittest.TestCase):
    def test_future_correction_late_data_and_publish_guards(self) -> None:
        # E-DATA-01/C-TIME-01/C-DATA-01..03/C-JOB-03.
        fx = configured()
        base_rows = [
            {"event_at": 10, "received_at": 10, "known_at": 10, "value": 100, "classification": "used"}
        ]
        v1 = fx.create_dataset("market", base_rows)
        fx.record_run("run-1", v1, cutoff_known_at=10)
        run_before = dict(fx.run_manifests["run-1"])

        corrected_rows = base_rows + [
            {"event_at": 9, "received_at": 20, "known_at": 20, "value": 99, "classification": "used"}
        ]
        v2 = fx.create_dataset("market", corrected_rows, parent_hash=v1["sha256"])
        self.assertNotEqual(v1["sha256"], v2["sha256"])
        self.assertEqual(fx.run_manifests["run-1"], run_before)
        self.assertEqual(v2["parent_hash"], v1["sha256"])
        with self.assertRaisesRegex(SafetyError, "FUTURE_OR_HOLDOUT_GUARD"):
            fx.guarded_rows(v2, cutoff_known_at=10)

        holdout = fx.create_dataset(
            "holdout",
            [{"event_at": 1, "received_at": 1, "known_at": 1, "value": 999, "classification": "holdout"}],
        )
        with self.assertRaisesRegex(SafetyError, "FUTURE_OR_HOLDOUT_GUARD"):
            fx.guarded_rows(holdout, cutoff_known_at=99)

        digest = fx.stage_artifact("candidate", b"partial-or-complete")
        self.assertNotIn("candidate", fx.published)  # interrupted publish is staged only
        with self.assertRaisesRegex(SafetyError, "VERIFICATION_HASH_MISMATCH"):
            fx.publish_artifact("candidate", digest, "0" * 64)
        self.assertNotIn("candidate", fx.published)
        fx.publish_artifact("candidate", digest, digest)
        self.assertEqual(fx.published["candidate"]["sha256"], digest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
