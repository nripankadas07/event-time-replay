# Research — 21 October 2026

Demand is **inferred**, not a verified request for this tool. An event log alone does not show when a window emits, retains state, corrects a result or drops a late event.

[Exact Most-stars search](https://github.com/search?q=event%20time%20streaming&type=repositories&s=stars&o=desc), observed 2026-10-21T06:19:17.897Z. Highest-star relevant comparable found in the inspected pool: `apache/flink`. This is not an exhaustive global ranking.

| Comparable | Stars | Last push | License metadata | Observed workflow |
| --- | ---: | --- | --- | --- |
| [apache/flink](https://github.com/apache/flink) | 26416 | 2026-10-20T19:00:34Z | Apache-2.0 | Distributed stateful stream/batch runtime. |
| [apache/beam](https://github.com/apache/beam) | 8688 | 2026-10-21T05:47:57Z | Apache-2.0 | Portable pipeline model with windows, watermarks, triggers and multiple runners. |
| [bytewax/bytewax](https://github.com/bytewax/bytewax) | 2056 | 2026-10-17T18:53:43Z | Apache-2.0 | Python stateful stream processing with runtime and recovery machinery. |

## Choice and tradeoffs

Replay explicit watermarks and tumbling-window events with accumulating emissions, late corrections, drop decisions and state eviction. kafka-offset-audit checks broker offset ranges; clock-quorum-window checks clocks. This replays changing per-window state under a stated event-time policy, with no broker or wall clock.

The established alternatives are broader and often the better choice for their supported ecosystems. This tool provides one bounded inspectable report with an invented example and no runtime dependencies. READMEs/docs were read for install and example workflow; competitor clean install, time to first useful result, reliability, support response and performance were not measured. Own tests prove only the documented subset. Stars are research context, not performance or adoption evidence.

Keyword search coverage is narrow: Avro results include generators/profilers, event-time results include general streaming platforms, inventory-expiry results include unrelated homelab/certificate inventory, and three-way results include plugins and unrelated scraped text. Known relevant established tools were added directly. Spreadsheet comparison uses Excelize rather than an obsolete GitHub openpyxl mirror.

[Exact metadata and sampled current issues/PRs](RESEARCH_PROVENANCE.json). The samples are context, not verified competitor defects or requests for our new tool. Relevant Avro compatibility, POI SharedFormula and Git merge-file source was inspected; standard algorithms are original reimplementations. Microsoft CellFormula and Beam semantics informed the bounded contracts. No third-party code, branding or prose is copied.

Primary references:
- https://beam.apache.org/documentation/programming-guide/#watermarks-and-late-data
