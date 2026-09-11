# Performance Engineering Standard

> **Purpose:** Define reusable rules for performance measurement, optimization, capacity, and performance-safe change.
>
> Performance targets belong in `NON_FUNCTIONAL_REQUIREMENTS.md`. This standard defines how engineers should reason about and verify them.

---

## 1. Core Principle

Performance work MUST be driven by evidence or explicit NFRs.

Do not optimize solely because code "looks slow."

First determine:
- user/business impact;
- expected workload;
- current measurement;
- bottleneck;
- acceptable tradeoff.

---

## 2. Define the Workload

Performance results MUST state relevant workload context.

Examples:
- requests/sec;
- concurrent users;
- message rate;
- data volume;
- payload size;
- cache warm/cold;
- region/network.

A latency number without workload context is incomplete.

---

## 3. Percentiles

Latency-sensitive systems SHOULD use percentiles.

Common:
- p50;
- p95;
- p99.

Average alone may hide poor tail latency.

Use only percentiles that matter operationally.

---

## 4. End-to-End vs Component

Measure at the correct boundary.

Examples:
- browser user experience;
- API server time;
- DB query time;
- provider latency;
- queue processing delay.

Do not attribute end-to-end latency to one component without measurement.

---

## 5. Baseline Before Optimization

Before a significant optimization:
1. capture baseline;
2. change one meaningful factor;
3. measure again;
4. compare;
5. verify correctness.

Avoid anecdotal "feels faster."

---

## 6. Profiling

Use profiling tools appropriate to the stack.

Profile:
- CPU;
- allocations;
- memory;
- blocking;
- I/O;
- database;
- frontend rendering.

Do not optimize based only on static code inspection when profiling can reveal the real bottleneck.

---

## 7. Database Performance

Investigate:
- query count;
- query plan;
- indexes;
- N+1;
- sort/hash spill;
- lock contention;
- connection pool;
- pagination.

Do not solve every slow query by adding an index.

Indexes have write/storage cost.

---

## 8. API Performance

API handlers SHOULD avoid:
- unnecessary sequential remote calls;
- repeated DB queries;
- unbounded serialization;
- large response payloads;
- blocking long-running work.

Parallel calls MAY reduce latency when:
- dependencies are independent;
- resource use is acceptable;
- error handling is clear.

---

## 9. Async Processing

Move work to background processing when:
- user does not need immediate completion;
- work is long-running;
- buffering/retry is useful.

Do not hide user-critical synchronous semantics behind async just to improve API latency.

---

## 10. Caching

Cache SHOULD be introduced only with explicit:

```text
source of truth
key
TTL
invalidation
staleness tolerance
failure behavior
```

Measure hit ratio and actual benefit where relevant.

Do not cache correctness bugs.

---

## 11. Memory

Memory usage SHOULD be bounded for user-controlled or large datasets.

Avoid:
- reading huge files fully into memory;
- loading unbounded tables;
- retaining large global caches;
- accidental object retention.

Streaming SHOULD be considered for large payloads.

---

## 12. CPU

CPU-heavy operations SHOULD:
- avoid request-thread starvation;
- use appropriate algorithms;
- move to worker/background when user outcome allows;
- be measured.

Do not micro-optimize trivial code while expensive database/network work dominates.

---

## 13. Algorithmic Complexity

For potentially large inputs, engineers SHOULD understand complexity.

Avoid obvious:
- nested scans over large collections;
- repeated full sorting;
- repeated parsing/computation.

Choose algorithms based on expected scale, not theoretical worst-case alone.

---

## 14. Connection Pools

Pool sizing SHOULD reflect:
- dependency capacity;
- instance count;
- workload;
- latency.

Increasing pool size can worsen downstream overload.

Monitor wait time and saturation.

---

## 15. Thread / Worker Pools

Worker concurrency SHOULD be bounded.

More threads/workers do not always improve throughput.

Consider:
- CPU cores;
- blocking I/O;
- DB connections;
- external quotas;
- queue backlog.

---

## 16. Batching

Batching MAY improve throughput for:
- writes;
- messages;
- external calls.

Batching SHOULD define:
- max batch size;
- latency tradeoff;
- partial failure;
- retry behavior.

Do not create huge batches that increase memory or recovery risk.

---

## 17. Frontend Performance

Frontend SHOULD consider:
- bundle size;
- code splitting;
- request waterfalls;
- render frequency;
- large lists;
- images/media;
- hydration/SSR cost;
- third-party scripts.

User experience metrics SHOULD be measured under realistic device/network conditions.

---

## 18. Bundle Size

New frontend dependencies SHOULD be evaluated for bundle/runtime cost.

Tree-shaking/code splitting SHOULD be used where ecosystem supports it.

Do not import an entire library for one small utility without considering alternatives.

---

## 19. Images and Media

Media SHOULD use:
- correct dimensions;
- compression;
- responsive variants;
- lazy loading when appropriate;
- CDN/object delivery where useful.

Avoid downloading oversized assets for small rendering contexts.

---

## 20. Large Lists

Use:
- pagination;
- virtualization;
- incremental rendering

when dataset size warrants it.

Do not rely on current demo data size.

---

## 21. Network

Reduce:
- unnecessary round trips;
- duplicated requests;
- chatty APIs;
- excessively large payloads.

Compression MAY be used for compressible payloads.

Do not compress already-compressed media unnecessarily.

---

## 22. Third-Party Scripts

Third-party frontend scripts SHOULD be evaluated for:
- performance;
- privacy;
- security;
- availability.

Defer/non-blocking load MAY be appropriate.

---

## 23. Startup Time

Applications/services with startup/readiness targets SHOULD measure:
- initialization;
- dependency connection;
- migrations;
- warmup.

Avoid expensive startup work that can be lazy/background without affecting readiness.

---

## 24. Cold Start

Serverless/on-demand environments SHOULD assess cold-start impact when relevant.

Possible mitigations:
- smaller artifact;
- fewer eager dependencies;
- provisioned capacity;
- architecture change.

Do not optimize cold start if it is not a real workload problem.

---

## 25. Capacity Planning

Projects SHOULD estimate capacity for important bottlenecks:

```text
requests
connections
messages
storage
bandwidth
provider quota
```

Capacity assumptions SHOULD be revisited as usage changes.

---

## 26. Load Testing

Load tests MUST define:
- workload model;
- ramp;
- steady state;
- duration;
- dataset;
- success thresholds.

Test environments SHOULD be representative enough for the decision.

---

## 27. Stress Testing

Stress tests MAY identify:
- saturation point;
- failure mode;
- recovery behavior.

Do not run uncontrolled stress tests against production unless explicitly approved and designed.

---

## 28. Soak Testing

Soak tests MAY detect:
- memory leaks;
- connection leaks;
- slow queue growth;
- resource exhaustion.

Use when long-running stability risk matters.

---

## 29. Performance Regression

Critical systems SHOULD have a way to detect significant performance regression.

Options:
- benchmark;
- CI microbenchmark;
- load test;
- production comparison.

Do not create noisy gates that block changes on meaningless variance.

---

## 30. Microbenchmarks

Microbenchmarks are useful for isolated hot code.

They MUST:
- use proper benchmark tooling;
- account for runtime warmup/JIT where applicable;
- not be treated as system performance evidence.

---

## 31. Performance vs Readability

Performance-critical code MAY be more complex when:
- benefit is measured;
- requirement justifies it;
- tests protect behavior;
- complexity is localized/documented.

Do not sacrifice maintainability for unmeasured gains.

---

## 32. Performance vs Consistency

Caching/read replicas/eventual consistency can improve performance but change semantics.

Such tradeoffs MUST be explicit in architecture/product behavior.

Do not silently weaken consistency for speed.

---

## 33. Performance vs Cost

Performance improvements SHOULD consider infrastructure cost.

Examples:
- more replicas;
- larger instances;
- premium CDN;
- additional cache.

The cheapest option is not always best, but cost is a real constraint.

---

## 34. Performance Telemetry

Important production paths SHOULD expose:
- latency;
- throughput;
- saturation;
- error rate.

Performance telemetry SHOULD allow comparison before/after deployments.

---

## 35. Performance Review Checklist

Review:
- NFR target;
- workload;
- measured baseline;
- bottleneck evidence;
- DB/network/runtime behavior;
- memory;
- frontend payload/rendering;
- capacity;
- regression evidence.

---

## 36. Exceptions

Performance standards MAY be lighter for prototypes.

Do not introduce complex optimization infrastructure before real need exists.
