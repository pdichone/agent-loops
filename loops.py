"""The same worker inside five loops. Each returns a Run: the code, why it stopped, what it cost.

    python loops.py naive         # run one loop once, print every iteration, save the code to runs/scratch/
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

from verify import verify
from worker import SPEC, work


@dataclass
class Run:
    code: str = ""
    iterations: int = 0
    stop: str = ""
    said_done: bool = False
    cost: float = 0.0
    input_tokens: int = 0
    trace: list = field(default_factory=list)  # one line per iteration

    def add(self, t, note=""):
        self.code, self.said_done = t.code or self.code, t.done
        self.iterations += 1
        self.cost += t.cost
        self.input_tokens += t.input_tokens
        self.trace.append(f"#{self.iterations} {'DONE' if t.done else 'CONTINUE':8} "
                          f"{t.input_tokens:>6} tokens in · ${self.cost:.4f} {note}")

    def finish(self, why: str) -> "Run":
        self.stop = why
        return self


# 0. No loop. One call, take what you get.
def one_shot() -> Run:
    run = Run()
    run.add(work([{"role": "user", "content": SPEC}]))
    return run.finish("one shot")


# 1. The naive loop: the model reviews its own work and decides when it's done.
def naive(max_iterations: int = 10) -> Run:
    run = Run()
    messages = [{"role": "user", "content": SPEC}]
    while run.iterations < max_iterations:  # without this line, a model that never says DONE never stops
        t = work(messages)
        run.add(t)
        if t.done:
            return run.finish("said done")
        messages += [{"role": "assistant", "content": t.text},
                     {"role": "user", "content": "Review your code against the spec. Fix anything that's wrong."}]
    return run.finish("max iterations")


# 2. The verified loop: the TESTS decide when it's done, and the failures go back to the model.
def verified(max_iterations: int = 10) -> Run:
    run = Run()
    messages = [{"role": "user", "content": SPEC}]
    while run.iterations < max_iterations:
        t = work(messages)
        report = verify(t.code)
        run.add(t, f"· tests {report.passed}/{report.total}")
        if report.green:
            return run.finish("tests pass")
        messages += [{"role": "assistant", "content": t.text},
                     {"role": "user", "content": f"{report.passed}/{report.total} tests pass. Failing:\n"
                                                 f"{report.failures}\n\nFix quote.py."}]
    return run.finish("max iterations")


# 3. Budgets: a hard cap on iterations AND dollars, and a breaker that stops a loop that stopped improving.
def budgeted(max_iterations: int = 8, max_dollars: float = 0.05, patience: int = 3) -> Run:
    run = Run()
    messages = [{"role": "user", "content": SPEC}]
    best, stale = -1, 0
    while True:
        if run.iterations >= max_iterations:
            return run.finish("max iterations")
        if run.cost >= max_dollars:
            return run.finish("budget")
        t = work(messages)
        report = verify(t.code)
        run.add(t, f"· tests {report.passed}/{report.total}")
        if report.green:
            return run.finish("tests pass")
        best, stale = (report.passed, 0) if report.passed > best else (best, stale + 1)
        if stale >= patience:
            return run.finish("no progress")
        messages += [{"role": "assistant", "content": t.text},
                     {"role": "user", "content": f"{report.passed}/{report.total} tests pass. Failing:\n"
                                                 f"{report.failures}\n\nFix quote.py."}]


LOOPS = {"one_shot": one_shot, "naive": naive, "verified": verified, "budgeted": budgeted}

if __name__ == "__main__":
    run = LOOPS[sys.argv[1] if len(sys.argv) > 1 else "naive"]()
    Path("runs/scratch").mkdir(parents=True, exist_ok=True)
    Path("runs/scratch/quote.py").write_text(run.code)
    print("\n".join(run.trace))
    visible = verify(run.code)
    print(f"\nstopped: {run.stop} · said done: {run.said_done} · ${run.cost:.4f}")
    print(f"visible tests {visible.passed}/{visible.total}")
