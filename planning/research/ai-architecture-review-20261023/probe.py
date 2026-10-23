"""Offline architecture probes; no product state, provider calls or benchmarks."""

from __future__ import annotations

import json
import operator
import sqlite3
import tempfile
from contextlib import closing
from importlib.metadata import version
from pathlib import Path
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


def parallel_shared_state() -> dict:
    class Shared(TypedDict):
        sender: str

    graph = StateGraph(Shared)
    graph.add_node("a", lambda _: {"sender": "a"})
    graph.add_node("b", lambda _: {"sender": "b"})
    for node in ("a", "b"):
        graph.add_edge(START, node)
        graph.add_edge(node, END)
    try:
        graph.compile().invoke({"sender": "initial"})
    except InvalidUpdateError:
        return {"expected_conflict_observed": True}
    raise AssertionError("Expected concurrent updates to a last-value channel to fail")


def parallel_isolated_state() -> dict:
    class Isolated(TypedDict):
        report_a: str
        report_b: str

    graph = StateGraph(Isolated)
    graph.add_node("a", lambda _: {"report_a": "evidence-a"})
    graph.add_node("b", lambda _: {"report_b": "evidence-b"})
    for node in ("a", "b"):
        graph.add_edge(START, node)
        graph.add_edge(node, END)
    result = graph.compile().invoke({"report_a": "", "report_b": ""})
    assert result == {"report_a": "evidence-a", "report_b": "evidence-b"}
    return {"separate_outputs_preserved": True}


def join_once() -> dict:
    class Outputs(TypedDict):
        values: Annotated[list[str], operator.add]

    def build(explicit_barrier: bool):
        graph = StateGraph(Outputs)
        for name in ("a", "a2", "b", "join"):
            graph.add_node(name, lambda _, name=name: {"values": [name]})
        graph.add_edge(START, "a")
        graph.add_edge(START, "b")
        graph.add_edge("a", "a2")
        if explicit_barrier:
            graph.add_edge(["a2", "b"], "join")
        else:
            graph.add_edge("a2", "join")
            graph.add_edge("b", "join")
        graph.add_edge("join", END)
        return graph.compile().invoke({"values": []})["values"].count("join")

    naive_count, barrier_count = build(False), build(True)
    assert naive_count == 2 and barrier_count == 1
    return {"separate_edges_join_count": naive_count, "explicit_barrier_join_count": barrier_count}


def checkpoint_identity_and_reopen() -> dict:
    class Items(TypedDict):
        items: Annotated[list[str], operator.add]

    builder = StateGraph(Items)
    builder.add_node("noop", lambda _: {})
    builder.add_edge(START, "noop")
    builder.add_edge("noop", END)
    shared = {"configurable": {"thread_id": "same-request-signature"}}
    separate = {"configurable": {"thread_id": "independent-run-id"}}
    with tempfile.TemporaryDirectory(prefix="tw-ai-review-") as directory:
        db_path = Path(directory) / "checkpoints.db"
        with closing(sqlite3.connect(db_path, check_same_thread=False)) as connection:
            saver = SqliteSaver(connection)
            saver.setup()
            graph = builder.compile(checkpointer=saver)
            graph.invoke({"items": ["run-a"]}, shared)
            reused = graph.invoke({"items": ["run-b"]}, shared)
            isolated = graph.invoke({"items": ["run-b"]}, separate)
            assert reused["items"] == ["run-a", "run-b"]
            assert isolated["items"] == ["run-b"]
        with closing(sqlite3.connect(db_path, check_same_thread=False)) as reopened:
            graph = builder.compile(checkpointer=SqliteSaver(reopened))
            assert graph.get_state(shared).values["items"] == ["run-a", "run-b"]
    return {"same_thread_accumulates": True, "separate_thread_isolated": True,
            "sqlite_reopen_preserves_state": True}


def interrupt_replays_node() -> dict:
    class Approval(TypedDict):
        approved: bool

    calls: list[str] = []

    def node(_):
        calls.append("non-idempotent-local-effect")
        approved = interrupt("fixture approval")
        return {"approved": approved}

    builder = StateGraph(Approval)
    builder.add_node("approval", node)
    builder.add_edge(START, "approval")
    builder.add_edge("approval", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "approval-fixture"}}
    graph.invoke({"approved": False}, config)
    assert len(calls) == 1
    result = graph.invoke(Command(resume=True), config)
    assert result["approved"] is True and len(calls) == 2
    return {"local_effect_count_before_and_after_resume": len(calls)}


if __name__ == "__main__":
    checks = {probe.__name__: probe() for probe in (
        parallel_shared_state, parallel_isolated_state, join_once,
        checkpoint_identity_and_reopen, interrupt_replays_node,
    )}
    print(json.dumps({"scope": "offline library fixtures, not product acceptance",
                      "langgraph_version": version("langgraph"),
                      "passed": len(checks), "checks": checks}, indent=2))
