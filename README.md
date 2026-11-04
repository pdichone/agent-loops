# Loop engineering, from scratch

One worker (a single Claude call that writes `quote.py`) inside five loops, measured. The task is a checkout-quote function for a made-up kitchenware shop (Kettleworks), from a spec that, like every real spec, leaves some business rules out. The test suite knows them; the model doesn't.

- **one shot**: one call, take what you get.
- **naive**: the model reviews its own work and decides when it's done.
- **verified**: the tests decide when it's done, and the failures go back to the model.
- **budgeted**: verified, plus a cap on iterations and dollars, and a breaker that stops a loop that stopped improving.
- **fresh**: budgeted, but every iteration starts a new conversation, rebuilt from the state the loop keeps (spec, current file, latest failures, notes): the "Ralph" pattern.

`task/test_hidden.py` is never shown to any loop. It stands in for production: it checks whether the code works, not whether it passes the tests the loop could see.

Video: [link]

## Build it step by step (the video)

Every step of the video is a git tag. Check out `step-0` and build along, or jump to any step.

| Tag | What you have |
|---|---|
| `step-0` | the task (`task/SPEC.md`, the tests), the worker (`worker.py`), the verifier (`verify.py`). No loop yet |
| `step-1` | `loops.py`: `one_shot` and the `naive` loop. It says DONE with tests failing |
| `step-2` | the `verified` loop. The tests decide. It gets stuck, and its context keeps growing |
| `step-3` | the `budgeted` loop (iterations, dollars, no-progress breaker), and the test message that tells the loop *how* it's wrong |
| `step-4` | the hidden tests, `bench.py`, and the outer loop: one new test and one spec line, written by a human |
| `step-5` | the `fresh` loop, and the full scoreboard |

```bash
git checkout step-3            # jump to a step
git diff step-2 step-3         # exactly what that step added
git checkout main              # the finished repo
```

## Run it

```bash
git clone https://github.com/pdichone/agent-loops && cd agent-loops
uv venv && source .venv/bin/activate && uv pip install -r pyproject.toml
cp .env.example .env    # ANTHROPIC_API_KEY

python worker.py                              # one call: writes runs/scratch/quote.py
python verify.py runs/scratch/quote.py        # run the visible tests against it
python loops.py naive                         # one loop, every iteration printed
python loops.py budgeted
python bench.py --runs 10                     # every loop 10 times: the scoreboard
WORKER_MODEL=claude-opus-5-5 EFFORT=medium python bench.py one_shot --runs 3
```

The worker defaults to Claude Haiku 5.5 at effort `low`: a loop run costs about half a cent, and `bench.py --runs 10` over all five loops is about 25 cents.

**The verifier runs model-written code on your machine** (in a temp folder, with a 60-second timeout). That's fine for this demo. In production, run it in a sandbox.

## Files

| File | What |
|---|---|
| `task/SPEC.md` | the spec the model sees. Incomplete on purpose |
| `task/test_visible.py` | the tests the loops can see (their failures go back to the model) |
| `task/test_hidden.py` | held-out tests, never shown to any loop |
| `reference/quote.py` | a correct solution. Never shown to the model; it proves the tests agree with each other |
| `worker.py` | one Claude call: spec (and feedback) in, `quote.py` and a DONE/CONTINUE claim out |
| `verify.py` | pytest in a temp folder: passed, total, and one line per failure |
| `loops.py` | the five loops |
| `bench.py` | runs loops N times in parallel, prints the scoreboard, appends every run to `runs/*.jsonl` |

## License

MIT
