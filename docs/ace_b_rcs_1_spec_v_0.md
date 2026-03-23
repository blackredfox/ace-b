# ACE-B / RCS-1 Specification v0.4
**Adaptive Cognitive Environment Benchmark**  
**Scenario:** Rule Change Survival (RCS-1)

---

## 1. Overview

RCS-1 evaluates whether an agent can:

- infer a latent rule from interaction,
- detect an unannounced rule change,
- revise its policy under uncertainty,
- recover performance with minimal perseveration,
- stabilize behavior after adaptation.

This benchmark targets **adaptive behavior under non-stationary environments**, not static task performance.

---

## 2. Design Principle

> Intelligence is evaluated through adaptation under change, not performance on fixed tasks.

Core loop being tested:

infer → exploit → detect failure → revise → stabilize

---

## 3. Scope (Refined)

### Included
- Procedural environment
- Hidden rule learning
- Mid-episode rule change
- Trajectory-level evaluation
- Multiple rule families
- Anti-cheating generation
- Baseline agents with distinct behaviors

### Explicitly NOT included
- Full AGI evaluation
- Natural language reasoning
- Multi-agent interaction (future work)

---

## 4. Core Evaluation Target

RCS-1 isolates one capability:

> **Latent rule revision under uncertainty**

This includes:
- hypothesis formation
- mismatch detection
- policy update
- resistance to obsolete-policy persistence

---

## 5. System Model

Agent → Environment → Scenario → Rule Change → Behavior → Metrics

---

## 6. Episode Structure

Each episode has four phases:

1. Warmup — rule inference
2. Mastery — stable performance
3. Hidden Change — rule switch without signal
4. Stabilization — recovery and convergence

---

## 7. Environment Design

### Observation

```json
{
  "step_id": int,
  "input": "string",
  "history": [...],
  "last_feedback": {"correct": bool}
}
```

### Action

```json
{
  "output": "string"
}
```

### Feedback

```json
{
  "correct": bool,
  "reward": float
}
```

---

## 8. Rule System (Critical Upgrade)

RCS-1 uses **multiple rule families** to avoid trivial solutions.

### Family A — Shift (baseline)
Simple cyclic transformation.

### Family B — Conditional
Rule depends on input or step condition.

### Family C — Stateful
Rule depends on previous state or outputs.

---

## 9. Rule Change Types

- Type A: parameter switch
- Type B: conditional structure change

---

## 10. Generator Requirements (Strengthened)

Generator MUST ensure:

- Learnability before switch
- Detectability after switch
- Non-trivial ambiguity
- No rule equivalence across phases
- Procedural diversity

---

## 11. Anti-Cheating (Mandatory)

- Procedural generation
- Hidden seeds
- Variable switch timing
- Multiple rule families
- Unseen combinations in test

---

## 12. Metrics (Refined)

### PCM — Pre-Change Mastery
Ensures real learning.

### CDL — Change Detection Lag
Measures detection latency.

### AHL — Adaptation Half-Life
Measures recovery speed.

### PCS — Post-Change Stability
Measures convergence quality.

### PR — Perseveration Rate (CORE METRIC)

Measures persistence of obsolete policy.

### EFF — Efficiency
Penalizes excessive exploration.

---

## 13. Key Metric Insight

RCS-1 separates:

- general error
- slow adaptation
- policy perseveration

This is the primary differentiator of the benchmark.

---

## 14. Scoring

Score = weighted combination of metrics.

Weights configurable.

---

## 15. Baseline Agents (Required)

1. Random agent
2. Static heuristic agent (no adaptation)
3. Adaptive agent (policy revision)

These must produce **distinct behavioral profiles**.

---

## 16. Validation Requirement

Benchmark must demonstrate:

- separation of agent types
- measurable adaptation behavior
- non-trivial failure modes

---

## 17. Non-Toy Requirement (New)

The benchmark must NOT be reducible to:

- lookup table
- fixed mapping
- trivial heuristic

This is enforced via:

- multiple rule families
- ambiguity before switch
- procedural variation

---

## 18. Real-World Mapping (Critical)

RCS-1 models a real failure class:

> persistence of outdated policy after environment change

Examples:
- stale routing logic
- outdated assumptions in agents
- incorrect step persistence (e.g. service workflows)

---

## 19. Output Requirements

System must produce:

- trajectory logs
- per-episode metrics
- aggregate scores

---

## 20. Reproducibility

All results must be reproducible via:

- config
- seed
- deterministic execution

---

## 21. Milestone Strategy (Updated)

### Milestone 1
- Shift family only
- Core metrics (PCM, CDL, PR)

### Milestone 2
- Add conditional family
- Add full metrics

### Milestone 3
- Add stateful family
- Strengthen generator

---

## 22. Definition of Done

- Runs locally
- Generates episodes
- Evaluates agents
- Shows behavioral differentiation

---

## 23. Positioning

RCS-1 is NOT a general AGI benchmark.

It is a focused benchmark for:

> latent rule revision under uncertainty

---

## 24. Key Claim (Final Form)

RCS-1 introduces explicit measurement of:

- detection latency
- adaptation dynamics
- policy perseveration

within a procedural environment.

---

