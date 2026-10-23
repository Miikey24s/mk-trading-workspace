"""Compare the same production analyst subgraphs at concurrency 1 and 4, offline.

Model latency is an artificial sleep; this is not an inference/capacity benchmark.
Run with the TradingAgents repository on PYTHONPATH and its locked environment.
"""

import hashlib
import json
import platform
import statistics
import time
from importlib.metadata import version

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from tradingagents.agents.state import AgentState
from tradingagents.graph.analyst_execution import AnalystNodeSpec
from tradingagents.graph.setup import _analyst_graph


def main():
    keys = ["market_report", "sentiment_report", "news_report", "fundamentals_report"]
    builder = StateGraph(AgentState)
    for key in keys:
        def analyst(_, key=key):
            time.sleep(0.05)
            return {key: f"deterministic-{key}", "messages": [AIMessage(content=key)]}

        spec = AnalystNodeSpec(key=key, agent_node=key, report_key=key)
        builder.add_node(key, _analyst_graph(spec, analyst, max_tool_rounds=2))
        builder.add_edge(START, key)
    builder.add_node("join", lambda _: {})
    builder.add_edge(keys, "join")
    builder.add_edge("join", END)
    graph = builder.compile()

    samples = {1: [], 4: []}
    digests = set()
    for limit in samples:
        graph.invoke({}, {"max_concurrency": limit})  # warm-up
    for sample in range(20):
        for limit in ((1, 4) if sample % 2 == 0 else (4, 1)):
            start = time.perf_counter()
            state = graph.invoke({}, {"max_concurrency": limit})
            samples[limit].append(round((time.perf_counter() - start) * 1000, 3))
            result = {key: state[key] for key in keys}
            digests.add(hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest())
    assert len(digests) == 1
    metrics = {
        str(limit): {"median_ms": round(statistics.median(times), 3),
                     "sample_p95_ms": sorted(times)[18], "samples_ms": times}
        for limit, times in samples.items()
    }
    print(json.dumps({"scope": "offline production subgraph topology with simulated 50ms I/O",
                      "python": platform.python_version(), "os": platform.platform(),
                      "langgraph": version("langgraph"), "tradingagents": version("tradingagents"),
                      "warmups_per_variant": 1, "samples_per_variant": 20,
                      "equal_output_sha256": next(iter(digests)), "metrics": metrics,
                      "median_speedup": round(statistics.median(samples[1]) / statistics.median(samples[4]), 3),
                      "limits": "No real model, quota, UI, CPU/RAM stress or Rust comparison measured."}, indent=2))


if __name__ == "__main__":
    main()
