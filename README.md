# event-time-replay

Replay explicit watermarks and tumbling-window events with accumulating emissions, late corrections, drop decisions and state eviction.

For streaming engineers reproducing a small watermark and late-event scenario offline.

## Quickstart

Python3.10+; no external service or runtime dependencies. Linux shell:

```sh
git clone https://github.com/nripankadas07/event-time-replay.git
cd event-time-replay
python -m venv .venv
. .venv/bin/activate
python -m pip install .
event-time-replay example.json
```

The invented window emits sum7, corrects it to11, then drops an event at expiry. [Expected JSON](example-output.json).

## Input and interpretation

Use the exact object in [example.json](example.json). Unknown keys, duplicate JSON keys and nonfinite numbers reject. The JSON file is read only, <=1MiB. Identifiers are nonempty strings <=128 characters; booleans are not integers.

One explicit global monotonic integer watermark; fixed windows [floor(t/size)*size,start+size), per key, exact integer count/sum. Up to5000 events; integers within +/-10^15, size>0 and lateness>=0. Own policy: first emission at watermark>=end, accepted later events emit accumulating corrections, purge/drop at watermark>=end+allowed_lateness. Timestamp<watermark is labeled late even if its window is not emitted. No implicit end flush. Unique event IDs required. No source connectors, inferred watermarks, sessions, sliding windows, processing-time triggers, recovery or full Beam/Flink/Bytewax equivalence.

Exit0: completed result without a finding/conflict; exit1: documented schema/shared-formula/stockout finding or merge conflict; exit2: malformed/unsupported input, stderr and no partial JSON report. Event-time drops are normal policy decisions and use exit0. A completed report is evidence only about the supplied model and supported subset. No automatic live-system changes.

## Verification

```sh
python -m unittest -v
python -m compileall -q event_time_replay.py
python -m pip wheel --no-deps . -w dist
```

Late update/drop/eviction boundary, negative timestamps, multi-key batch oracle, zero lateness, no flush, duplicate IDs and backward-watermark rejection. [Validation record](VALIDATION.md). CI checks Python3.10/3.12/3.14 and a wheel-installed console from outside the checkout. Windows/macOS and production-size workloads are not verified. No benchmark or superiority claim.

## Scope and provenance

Alpha utility, original AI-assisted implementation and invented fixtures. Standard algorithms were reimplemented; no third-party implementation/prose copied. MIT. [Candidate brief](BRIEF.json), [dated research and alternatives](RESEARCH.md), [support](SUPPORT.md), [contribution guide](CONTRIBUTING.md), [security](SECURITY.md).

kafka-offset-audit checks broker offset ranges; clock-quorum-window checks clocks. This replays changing per-window state under a stated event-time policy, with no broker or wall clock.
