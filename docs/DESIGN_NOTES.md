# Design Notes and Ideas

These are exploratory ideas, not accepted architecture or MVP commitments.

## Local task profiler

A small local model may be useful as an optional **Task Profiler** for free-form requests.

The profiler would not choose a concrete provider/model itself. Its role is to transform an ambiguous user request into a structured task profile, for example:

```json
{
  "family": "creative_writing",
  "complexity": "high",
  "fidelity": "high",
  "reasoning": "low",
  "risk": "low"
}
```

The Router would then combine that profile with:

- model registry metadata;
- runtime health;
- quota/cooldown state;
- cost policy;
- quality history;
- diversity constraints.

### Profiler should be skipped when unnecessary

Known workloads should remain explicit and bypass profiling.

Examples:

- Job Hunter vacancy matcher;
- Job Hunter cover letter;
- OSINT scout;
- OSINT judge.

The profiler is most useful for generic or free-form workloads where the project cannot classify the request reliably in advance.

### Possible cascade

A future routing flow could be:

```text
request
  ↓
explicit workload?
  ├─ yes → route directly
  └─ no
       ↓
generic rules / known profile?
  ├─ yes → route
  └─ no
       ↓
small local Task Profiler
       ↓
Task Profile
       ↓
Router
```

A stronger fallback profiler may be considered later for low-confidence/invalid classifications, but it should not be mandatory for MVP.

## Small local model sizing

For the profiler role, a very small quantized instruct model may be enough.

Initial exploration target:

- 0.5B–1.5B parameters;
- 4-bit quantization;
- short context (roughly 2k–4k);
- short structured JSON output;
- one request at a time;
- short keep-alive or unload-on-idle behavior.

A 2–3B model should only be considered if smaller models fail workload-classification quality tests.

The profiler should be benchmarked on real Gateway workloads rather than selected theoretically.

## Xiaomi 11T Pro as an edge inference node

An unused rooted Xiaomi 11T Pro may be practical as a dedicated local inference node.

Possible role:

```text
Xiaomi 11T Pro
→ rooted Android
→ Termux / native llama.cpp-style server
→ small Task Profiler
→ network or USB connection
→ AI Gateway
```

Potential advantages:

- keeps profiler memory/CPU load away from the Lenovo host;
- zero marginal API cost;
- physically separate compute;
- can remain connected over USB for power and transport;
- root access may allow stronger control over Android/MIUI power management.

### USB transport idea

If the inference server listens on the phone, USB/ADB forwarding could expose it to a host as a loopback endpoint.

Conceptually:

```text
phone:8080
   ↓ USB
host:127.0.0.1:<forwarded-port>
   ↓
Gateway local provider
```

Exact transport and Android tooling are implementation details to validate later.

## Edge/local node reliability class

Phones, laptops and home machines should not be treated as always-on infrastructure even when rooted or carefully configured.

They should be modeled as **ephemeral / opportunistic local capacity**.

Expected behavior:

- automatic health checks;
- fast removal from the eligible pool when unreachable;
- no long blocking retries;
- no critical dependency on the node;
- automatic return to the pool after recovery;
- workloads with explicit profiles must continue without the profiler node.

This resource class may later apply to:

- rooted Android devices;
- laptops;
- home desktops;
- temporary local GPU hosts;
- LAN Ollama nodes.

The Gateway itself and critical routing state should remain on more reliable infrastructure.

## Training / adaptation idea

Do not train a profiler from scratch initially.

A practical progression could be:

1. start with a small instruct model and strict output schema;
2. collect real workload/profile examples;
3. retain explicit known workload labels from Job Hunter and OSINT as high-quality training data;
4. record profiler predictions and validation outcomes;
5. correct poor labels;
6. consider LoRA/fine-tuning only after enough representative examples exist.

Job Hunter and OSINT are useful bootstrap datasets because many calls already have known semantic roles.

Potential training signals:

- prompt/request;
- project;
- declared workload;
- profiler prediction;
- selected route;
- structured-output validity;
- task-specific validator result;
- human/project override;
- fallback history.

This should remain an optional future optimization, not an MVP dependency.
