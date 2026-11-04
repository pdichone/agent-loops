"""Run every loop N times and print the scoreboard.

    python bench.py --runs 10
    python bench.py one_shot --runs 5                    # just one loop
    WORKER_MODEL=claude-opus-5-5 python bench.py one_shot --runs 5
"""

import argparse
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from loops import LOOPS
from verify import verify
from worker import EFFORT, MODEL


def trial(name: str) -> dict:
    run = LOOPS[name]()
    v, h = verify(run.code), verify(run.code, hidden=True)
    return {"loop": name, "stop": run.stop, "said_done": run.said_done, "iterations": run.iterations,
            "cost": run.cost, "input_tokens": run.input_tokens, "visible": [v.passed, v.total],
            "hidden": [h.passed, h.total], "trace": run.trace, "hidden_failures": h.failures}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("loops", nargs="*", default=list(LOOPS))
    p.add_argument("--runs", type=int, default=5)
    a = p.parse_args()

    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(trial, [n for n in a.loops for _ in range(a.runs)]))

    out = Path("runs") / f"{MODEL}-{EFFORT}.jsonl"
    out.parent.mkdir(exist_ok=True)
    with out.open("a") as f:
        f.writelines(json.dumps(r) + "\n" for r in results)

    print(f"{MODEL}, effort {EFFORT}, {a.runs} runs per loop\n")
    print(f"{'loop':10} {'all visible green':>18} {'hidden pass':>12} {'false DONE':>11} {'iters':>6} {'$/run':>8}  stopped")
    for name in a.loops:
        rs = [r for r in results if r["loop"] == name]
        green = sum(r["visible"][0] == r["visible"][1] for r in rs)
        hidden = sum(r["hidden"][0] for r in rs) / sum(r["hidden"][1] for r in rs)
        false_done = sum(r["said_done"] and r["visible"][0] < r["visible"][1] for r in rs)
        stops = ", ".join(f"{k} {v}" for k, v in Counter(r["stop"] for r in rs).most_common())
        print(f"{name:10} {green:>14}/{len(rs):<3} {hidden:>12.0%} {false_done:>7}/{len(rs):<3} "
              f"{sum(r['iterations'] for r in rs) / len(rs):>6.1f} {sum(r['cost'] for r in rs) / len(rs):>8.4f}  {stops}")
    print(f"\nsaved to {out}")
