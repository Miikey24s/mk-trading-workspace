from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import controller


class LedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db_path = self.root / "ledger.sqlite3"
        self.conn = controller.connect(self.db_path)
        controller.init_db(self.conn, run_id="run-test", plan_hash="plan-hash", scope="VALIDATION_ONLY")
        self.gen = controller.acquire_initial_owner(self.conn, locator="test-parent")

    def tearDown(self) -> None:
        self.conn.close()
        self.temp.cleanup()

    def add_ready(self, task_id: str = "CO-01") -> None:
        controller.add_task(
            self.conn,
            task_id=task_id,
            spec_hash="spec",
            dependencies=[],
            allowed_files=["fixture"],
            acceptance=["pass"],
            owner_generation=self.gen,
            status="ready",
        )

    def verification_details(self, *, exit_code: int = 0) -> dict[str, object]:
        return {
            "test_hash": "test-hash",
            "input_hashes": {"fixture": "fixture-hash"},
            "test_scope": "focused fixture checks",
            "expected_outcomes": ["deterministic expected result"],
            "exit_code": exit_code,
        }

    def test_unique_task_and_cas_transition(self) -> None:
        controller.add_task(
            self.conn,
            task_id="CO-01",
            spec_hash="spec",
            dependencies=[],
            allowed_files=["fixture"],
            acceptance=["pass"],
            owner_generation=self.gen,
            status="planned",
        )
        with self.assertRaises(sqlite3.IntegrityError):
            controller.add_task(
                self.conn,
                task_id="CO-01",
                spec_hash="spec",
                dependencies=[],
                allowed_files=["fixture"],
                acceptance=["pass"],
                owner_generation=self.gen,
                status="planned",
            )
        controller.transition_task(
            self.conn,
            task_id="CO-01",
            expected_status="planned",
            expected_revision=1,
            new_status="ready",
            owner_generation=self.gen,
            reason="fixture",
        )
        with self.assertRaises(controller.ConflictError):
            controller.transition_task(
                self.conn,
                task_id="CO-01",
                expected_status="planned",
                expected_revision=1,
                new_status="ready",
                owner_generation=self.gen,
                reason="stale cas",
            )

    def test_child_cannot_mutate_authoritative_state(self) -> None:
        with self.assertRaises(controller.AuthorityError):
            controller.add_task(
                self.conn,
                task_id="BAD",
                spec_hash="x",
                dependencies=[],
                allowed_files=[],
                acceptance=[],
                owner_generation=self.gen,
                actor_role="child",
            )

    def test_acceptance_cannot_be_seeded_or_transitioned_directly(self) -> None:
        with self.assertRaises(ValueError):
            controller.add_task(
                self.conn,
                task_id="BAD-ACCEPT",
                spec_hash="x",
                dependencies=[],
                allowed_files=[],
                acceptance=[],
                owner_generation=self.gen,
                status="accepted",
            )
        self.add_ready("CO-01")
        with self.assertRaises(controller.ConflictError):
            controller.transition_task(
                self.conn,
                task_id="CO-01",
                expected_status="ready",
                expected_revision=1,
                new_status="accepted",
                owner_generation=self.gen,
                reason="bypass",
            )

    def test_dependency_gate_blocks_ready_and_dispatch_until_accepted(self) -> None:
        controller.add_task(
            self.conn,
            task_id="PARENT",
            spec_hash="p",
            dependencies=[],
            allowed_files=[],
            acceptance=[],
            owner_generation=self.gen,
            status="planned",
        )
        with self.assertRaises(controller.ConflictError):
            controller.add_task(
                self.conn,
                task_id="BAD-READY",
                spec_hash="c",
                dependencies=["PARENT"],
                allowed_files=[],
                acceptance=[],
                owner_generation=self.gen,
                status="ready",
            )
        controller.add_task(
            self.conn,
            task_id="CHILD",
            spec_hash="c",
            dependencies=["PARENT"],
            allowed_files=[],
            acceptance=[],
            owner_generation=self.gen,
            status="planned",
        )
        with self.assertRaises(controller.ConflictError):
            controller.transition_task(
                self.conn,
                task_id="CHILD",
                expected_status="planned",
                expected_revision=1,
                new_status="ready",
                owner_generation=self.gen,
                reason="dependency not accepted",
            )
        self.conn.execute("UPDATE tasks SET status='ready' WHERE task_id='CHILD'")
        with self.assertRaises(controller.ConflictError):
            controller.prepare_attempt(
                self.conn,
                task_id="CHILD",
                attempt_id="child-a1",
                owner_generation=self.gen,
                expected_task_revision=1,
                input_hash="input",
                base_revision="base",
                namespace="child-ns",
            )

    def test_generic_control_transition_cannot_skip_state_machine(self) -> None:
        self.add_ready("CO-01")
        with self.assertRaises(controller.ConflictError):
            controller.transition_task(
                self.conn,
                task_id="CO-01",
                expected_status="ready",
                expected_revision=1,
                new_status="running",
                owner_generation=self.gen,
                reason="illegal shortcut",
            )

    def test_prepare_attempt_prevents_duplicate_active_dispatch(self) -> None:
        self.add_ready()
        controller.prepare_attempt(
            self.conn,
            task_id="CO-01",
            attempt_id="a1",
            owner_generation=self.gen,
            expected_task_revision=1,
            input_hash="same-input",
            base_revision="base",
            namespace="ns-a",
        )
        task_status = self.conn.execute("SELECT status FROM tasks WHERE task_id='CO-01'").fetchone()["status"]
        self.assertEqual(task_status, "dispatch_prepared")
        event_count = self.conn.execute(
            "SELECT COUNT(*) AS n FROM events WHERE task_id='CO-01' AND event_type='dispatch_prepared'"
        ).fetchone()["n"]
        self.assertEqual(event_count, 1)
        self.conn.execute("UPDATE tasks SET status='ready' WHERE task_id='CO-01'")
        with self.assertRaises(sqlite3.IntegrityError):
            controller.prepare_attempt(
                self.conn,
                task_id="CO-01",
                attempt_id="a2",
                owner_generation=self.gen,
                expected_task_revision=2,
                input_hash="same-input",
                base_revision="base",
                namespace="ns-b",
            )

    def test_prepare_attempt_rolls_back_if_later_task_update_fails(self) -> None:
        self.add_ready("ROLLBACK")
        self.conn.executescript(
            """
            CREATE TRIGGER fail_dispatch_update
            BEFORE UPDATE OF status ON tasks
            WHEN NEW.task_id = 'ROLLBACK' AND NEW.status = 'dispatch_prepared'
            BEGIN
                SELECT RAISE(ABORT, 'forced dispatch update failure');
            END;
            """
        )
        with self.assertRaises(sqlite3.IntegrityError):
            controller.prepare_attempt(
                self.conn,
                task_id="ROLLBACK",
                attempt_id="rollback-a1",
                owner_generation=self.gen,
                expected_task_revision=1,
                input_hash="rollback-input",
                base_revision="base",
                namespace="rollback-ns",
            )
        self.assertIsNone(
            self.conn.execute("SELECT 1 FROM attempts WHERE attempt_id='rollback-a1'").fetchone()
        )
        task = self.conn.execute(
            "SELECT status,revision FROM tasks WHERE task_id='ROLLBACK'"
        ).fetchone()
        self.assertEqual(dict(task), {"status": "ready", "revision": 1})
        event_count = self.conn.execute(
            "SELECT COUNT(*) AS n FROM events WHERE task_id='ROLLBACK' AND event_type='dispatch_prepared'"
        ).fetchone()["n"]
        self.assertEqual(event_count, 0)

    def test_revision_cas_rejects_stale_revision_when_status_matches(self) -> None:
        controller.add_task(
            self.conn,
            task_id="REV",
            spec_hash="spec",
            dependencies=[],
            allowed_files=[],
            acceptance=[],
            owner_generation=self.gen,
            status="planned",
        )
        controller.transition_task(
            self.conn,
            task_id="REV",
            expected_status="planned",
            expected_revision=1,
            new_status="ready",
            owner_generation=self.gen,
            reason="first transition",
        )
        with self.assertRaises(controller.ConflictError):
            controller.transition_task(
                self.conn,
                task_id="REV",
                expected_status="ready",
                expected_revision=1,
                new_status="planned",
                owner_generation=self.gen,
                reason="stale revision",
            )

    def test_failed_evidence_blocks_integration_even_if_pass_exists(self) -> None:
        self.add_ready()
        controller.prepare_attempt(
            self.conn,
            task_id="CO-01",
            attempt_id="a-fail",
            owner_generation=self.gen,
            expected_task_revision=1,
            input_hash="in-fail",
            base_revision="base",
            namespace="ns",
        )
        controller.record_candidate(
            self.conn,
            attempt_id="a-fail",
            artifact_path="artifact",
            artifact_hash="candidate-fail",
            provenance={},
            owner_generation=self.gen,
        )
        controller.record_verification(
            self.conn,
            verification_id="v-pass",
            attempt_id="a-fail",
            candidate_hash="candidate-fail",
            verifier="unit",
            verifier_version="1",
            result="pass",
            details=self.verification_details(),
            owner_generation=self.gen,
        )
        controller.record_verification(
            self.conn,
            verification_id="v-fail",
            attempt_id="a-fail",
            candidate_hash="candidate-fail",
            verifier="unit-2",
            verifier_version="1",
            result="fail",
            details=self.verification_details(exit_code=1),
            owner_generation=self.gen,
        )
        controller.record_review(
            self.conn,
            review_id="r-pass",
            attempt_id="a-fail",
            candidate_hash="candidate-fail",
            reviewer_locator="reviewer",
            verdict="pass",
            findings=[],
            owner_generation=self.gen,
        )
        with self.assertRaises(controller.ConflictError):
            controller.prepare_integration_intent(
                self.conn,
                task_id="CO-01",
                attempt_id="a-fail",
                candidate_hash="candidate-fail",
                target_base="base",
                owner_generation=self.gen,
            )

    def test_integration_cannot_attach_candidate_to_other_task(self) -> None:
        self.add_ready("A")
        self.add_ready("B")
        controller.prepare_attempt(
            self.conn,
            task_id="A",
            attempt_id="a-cross",
            owner_generation=self.gen,
            expected_task_revision=1,
            input_hash="cross",
            base_revision="base",
            namespace="ns",
        )
        controller.record_candidate(
            self.conn,
            attempt_id="a-cross",
            artifact_path="artifact",
            artifact_hash="cross-hash",
            provenance={},
            owner_generation=self.gen,
        )
        controller.record_verification(
            self.conn,
            verification_id="v-cross",
            attempt_id="a-cross",
            candidate_hash="cross-hash",
            verifier="unit",
            verifier_version="1",
            result="pass",
            details=self.verification_details(),
            owner_generation=self.gen,
        )
        controller.record_review(
            self.conn,
            review_id="r-cross",
            attempt_id="a-cross",
            candidate_hash="cross-hash",
            reviewer_locator="reviewer",
            verdict="pass",
            findings=[],
            owner_generation=self.gen,
        )
        with self.assertRaises(controller.ConflictError):
            controller.prepare_integration_intent(
                self.conn,
                task_id="B",
                attempt_id="a-cross",
                candidate_hash="cross-hash",
                target_base="base",
                owner_generation=self.gen,
            )

    def test_late_result_cannot_overwrite_accepted_task(self) -> None:
        self.add_ready()
        controller.prepare_attempt(
            self.conn,
            task_id="CO-01",
            attempt_id="a1",
            owner_generation=self.gen,
            expected_task_revision=1,
            input_hash="in",
            base_revision="base",
            namespace="ns",
        )
        controller.record_candidate(
            self.conn,
            attempt_id="a1",
            artifact_path="artifact",
            artifact_hash="candidate-hash",
            provenance={"kind": "fixture"},
            owner_generation=self.gen,
        )
        controller.record_verification(
            self.conn,
            verification_id="v1",
            attempt_id="a1",
            candidate_hash="candidate-hash",
            verifier="unit",
            verifier_version="1",
            result="pass",
            details=self.verification_details(),
            owner_generation=self.gen,
        )
        controller.record_review(
            self.conn,
            review_id="r1",
            attempt_id="a1",
            candidate_hash="candidate-hash",
            reviewer_locator="fresh-reviewer",
            verdict="pass",
            findings=[],
            owner_generation=self.gen,
        )
        controller.prepare_integration_intent(
            self.conn,
            task_id="CO-01",
            attempt_id="a1",
            candidate_hash="candidate-hash",
            target_base="base",
            owner_generation=self.gen,
        )
        controller.finalize_after_promotion(
            self.conn,
            task_id="CO-01",
            observed_revision="candidate-hash",
            owner_generation=self.gen,
        )
        with self.assertRaises(controller.ConflictError):
            controller.mark_attempt_uncertain(
                self.conn,
                attempt_id="a1",
                reason="late disconnect",
                owner_generation=self.gen,
            )
        status = self.conn.execute("SELECT status FROM tasks WHERE task_id='CO-01'").fetchone()["status"]
        self.assertEqual(status, "accepted")

    def test_promotion_before_finalize_recovery(self) -> None:
        self.add_ready("CO-02")
        controller.prepare_attempt(
            self.conn,
            task_id="CO-02",
            attempt_id="a2",
            owner_generation=self.gen,
            expected_task_revision=1,
            input_hash="in-2",
            base_revision="base",
            namespace="ns-2",
        )
        controller.record_candidate(
            self.conn,
            attempt_id="a2",
            artifact_path="artifact-2",
            artifact_hash="rev-2",
            provenance={"kind": "fixture"},
            owner_generation=self.gen,
        )
        controller.record_verification(
            self.conn,
            verification_id="v2",
            attempt_id="a2",
            candidate_hash="rev-2",
            verifier="unit",
            verifier_version="1",
            result="pass",
            details=self.verification_details(),
            owner_generation=self.gen,
        )
        controller.record_review(
            self.conn,
            review_id="r2",
            attempt_id="a2",
            candidate_hash="rev-2",
            reviewer_locator="fresh-reviewer",
            verdict="pass",
            findings=[],
            owner_generation=self.gen,
        )
        controller.prepare_integration_intent(
            self.conn,
            task_id="CO-02",
            attempt_id="a2",
            candidate_hash="rev-2",
            target_base="base",
            owner_generation=self.gen,
        )
        with self.assertRaises(controller.ConflictError):
            controller.finalize_after_promotion(
                self.conn,
                task_id="CO-02",
                observed_revision="wrong-revision",
                owner_generation=self.gen,
            )
        controller.finalize_after_promotion(
            self.conn,
            task_id="CO-02",
            observed_revision="rev-2",
            owner_generation=self.gen,
        )
        row = self.conn.execute("SELECT status,accepted_revision FROM tasks WHERE task_id='CO-02'").fetchone()
        self.assertEqual(dict(row), {"status": "accepted", "accepted_revision": "rev-2"})

    def test_snapshot_checksum_rejects_torn_or_modified_export(self) -> None:
        self.add_ready()
        snap, checksum = controller.export_snapshot(self.conn, self.root / "state.json")
        loaded = controller.validate_snapshot(snap, checksum)
        self.assertEqual(loaded["snapshot_schema"], 1)
        snap.write_text(json.dumps({"partial": True}), encoding="utf-8")
        with self.assertRaises(controller.ConflictError):
            controller.validate_snapshot(snap, checksum)

    def test_prepared_dispatch_survives_reopen_and_blocks_duplicate_dispatch(self) -> None:
        self.add_ready("PERSIST")
        controller.prepare_attempt(
            self.conn,
            task_id="PERSIST",
            attempt_id="persist-a1",
            owner_generation=self.gen,
            expected_task_revision=1,
            input_hash="persist-input",
            base_revision="base",
            namespace="persist-ns",
        )
        self.conn.close()
        self.conn = controller.connect(self.db_path)
        task = self.conn.execute(
            "SELECT status,revision FROM tasks WHERE task_id='PERSIST'"
        ).fetchone()
        self.assertEqual(dict(task), {"status": "dispatch_prepared", "revision": 2})
        attempt = self.conn.execute(
            "SELECT status FROM attempts WHERE attempt_id='persist-a1'"
        ).fetchone()
        self.assertEqual(attempt["status"], "dispatch_prepared")
        with self.assertRaises(controller.ConflictError):
            controller.prepare_attempt(
                self.conn,
                task_id="PERSIST",
                attempt_id="persist-a2",
                owner_generation=self.gen,
                expected_task_revision=2,
                input_hash="persist-input",
                base_revision="base",
                namespace="persist-ns-2",
            )

    def test_takeover_requires_confirmation_and_fences_old_generation(self) -> None:
        with self.assertRaises(controller.AuthorityError):
            controller.takeover_owner(
                self.conn,
                expected_generation=1,
                expected_locator="test-parent",
                new_locator="fresh-parent",
                confirmed_old_inactive=False,
            )
        generation = controller.takeover_owner(
            self.conn,
            expected_generation=1,
            expected_locator="test-parent",
            new_locator="fresh-parent",
            confirmed_old_inactive=True,
        )
        self.assertEqual(generation, 2)
        with self.assertRaises(controller.AuthorityError):
            controller.add_task(
                self.conn,
                task_id="FENCED-STALE",
                spec_hash="spec",
                dependencies=[],
                allowed_files=[],
                acceptance=[],
                owner_generation=1,
                status="planned",
            )
        controller.add_task(
            self.conn,
            task_id="FENCED",
            spec_hash="spec",
            dependencies=[],
            allowed_files=[],
            acceptance=[],
            owner_generation=generation,
            status="planned",
        )
        with self.assertRaises(controller.AuthorityError):
            controller.transition_task(
                self.conn,
                task_id="FENCED",
                expected_status="planned",
                expected_revision=1,
                new_status="ready",
                owner_generation=1,
                reason="stale owner",
            )

    def test_stale_snapshot_rejected_after_attempt_running_mutation(self) -> None:
        self.add_ready("AFTER-SNAPSHOT")
        controller.prepare_attempt(
            self.conn,
            task_id="AFTER-SNAPSHOT",
            attempt_id="after-snapshot-a1",
            owner_generation=self.gen,
            expected_task_revision=1,
            input_hash="after-snapshot-input",
            base_revision="base",
            namespace="after-snapshot-ns",
        )
        snap, checksum = controller.export_snapshot(self.conn, self.root / "stale.json")
        old_revision = controller.validate_snapshot(snap, checksum)["state_revision"]
        controller.mark_attempt_running(
            self.conn,
            attempt_id="after-snapshot-a1",
            owner_generation=self.gen,
            child_locator="child",
            route_locator="route",
        )
        current_revision = int(self.conn.execute("SELECT COALESCE(MAX(seq),0) AS seq FROM events").fetchone()["seq"])
        self.assertGreater(current_revision, old_revision)
        with self.assertRaises(controller.ConflictError):
            controller.validate_snapshot(snap, checksum, minimum_event_seq=current_revision)


if __name__ == "__main__":
    unittest.main(verbosity=2)
