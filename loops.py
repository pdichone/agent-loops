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


LOOPS = {"one_shot": one_shot, "naive": naive}

if __name__ == "__main__":
    run = LOOPS[sys.argv[1] if len(sys.argv) > 1 else "naive"]()
    Path("runs/scratch").mkdir(parents=True, exist_ok=True)
    Path("runs/scratch/quote.py").write_text(run.code)
    print("\n".join(run.trace))
    visible = verify(run.code)
    print(f"\nstopped: {run.stop} · said done: {run.said_done} · ${run.cost:.4f}")
    print(f"visible tests {visible.passed}/{visible.total}")
