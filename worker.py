"""The worker: ONE Claude call that writes quote.py. No loop in here. The loop is what we engineer.

    python worker.py            # one shot: write quote.py from the spec, save it to runs/scratch/
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("WORKER_MODEL", "claude-haiku-5-5")
EFFORT = os.getenv("EFFORT", "low")
# $ per million tokens, input / output (platform.claude.com pricing, 2026-11-04)
PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.00, 10.00),
          "claude-opus-5-5": (4.00, 20.00)}

TASK = Path(__file__).parent / "task"
SPEC = (TASK / "SPEC.md").read_text()
SYSTEM = """You are a Python developer. Implement the spec you are given.
Reply with the complete file quote.py in a single ```python block. No other code blocks.
Then end with exactly one line: STATUS: DONE if you are confident the file fully meets the spec,
or STATUS: CONTINUE if it still needs work."""

client = Anthropic(timeout=120.0)  # the SDK default is 10 minutes per try: one hung call stalls the whole loop


@dataclass
class Turn:
    text: str            # everything the model said
    code: str            # the quote.py it wrote ("" if it wrote none)
    done: bool           # did it CLAIM to be done?
    input_tokens: int
    output_tokens: int

    @property
    def cost(self) -> float:
        i, o = PRICES[MODEL]
        return (self.input_tokens * i + self.output_tokens * o) / 1_000_000


def work(messages: list) -> Turn:
    r = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        output_config={"effort": EFFORT},
        messages=messages,
    )
    text = "".join(b.text for b in r.content if b.type == "text")
    code = re.search(r"```python\n(.*?)```", text, re.S)
    return Turn(text, code.group(1) if code else "", "STATUS: DONE" in text,
                r.usage.input_tokens, r.usage.output_tokens)


if __name__ == "__main__":
    t = work([{"role": "user", "content": SPEC}])
    out = Path("runs/scratch/quote.py")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(t.code)
    print(t.text.strip().splitlines()[-1])
    print(f"[{MODEL}, effort {EFFORT}] wrote {out} ({len(t.code.splitlines())} lines) · "
          f"{t.input_tokens} in / {t.output_tokens} out · ${t.cost:.4f}")
