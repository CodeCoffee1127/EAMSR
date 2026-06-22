# EAMSR Annotation Protocol v1.0

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Date** | 2026-06-15 |
| **Scope** | Dual-agent annotation protocol for EAMSR-Bench mission admission decisions |
| **Status** | Active |
| **References** | Method Doc Section 3.1--3.3, Experiment Doc Section 4.1.1 |

---

## Table of Contents

1. [Terminology](#2-terminology)
2. [Dual-Agent Annotation Flow](#3-dual-agent-annotation-flow)
3. [Intersection Arbitration Rules](#4-intersection-arbitration-rules)
4. [Claim_H Identification Rules](#5-claim_h-llm-hypothesis-identification-rules)
5. [Evidence Support Determination](#6-evidence-support-determination)
6. [Annotation Quality Checklist](#7-annotation-quality-checklist)
7. [Conflict Resolution Escalation](#8-conflict-resolution-escalation)

---

## 1. Document Header

### 1.1 Purpose

This document defines the complete annotation protocol for dual-agent labeling of the EAMSR-Bench dataset. Every sample in the benchmark (120 natural language UAV mission instructions across 6 scenarios, 6 risk categories, and 3 language complexity types) must pass through the three-stage annotation pipeline described herein before being admitted into the ground-truth corpus.

### 1.2 Scope

This protocol governs:

- Construction of Mission Admission Contracts (`MAC`) from raw natural language instructions
- Dual independent annotation by Agent A and Agent B
- Intersection-based arbitration and conflict resolution
- Identification and handling of LLM-generated hypotheses (`Claim_H`)
- Evidence support determination and mismatch resolution
- Quality assurance and escalation procedures

### 1.3 References

| Document | Sections | Description |
|---|---|---|
| Method Doc | 3.1--3.3 | Formal contract semantics, proof obligations, consequence signatures |
| Experiment Doc | 4.1.1 | Benchmark construction, scenario definitions, risk taxonomy |

---

## 2. Terminology

### 2.1 Core Constructs

**Mission Admission Contract (MAC)**
> A structured formal object that encodes all requirements, constraints, assumptions, and evidence bindings extracted from a natural language UAV mission instruction `x`. The MAC is the central artifact produced during annotation and serves as the basis for the admission decision.

Structure:
```
MAC = {
  contract_id: str,
  source_instruction: str,
  clauses: Clause[],
  consequence_signature: χ(C),
  admission_decision: ACCEPT | CLARIFY | REJECT,
  risk_category: T1 | T2 | T3 | T4 | T5 | T6,
  audit_trail: AuditEntry[]
}
```

**Evidence Base (E)**
> The repository of all verifiable facts available to the annotation system. Comprises three sub-components:
> - `E_user`: facts explicitly stated in the natural language instruction `x`
> - `E_ctx`: facts drawn from the scenario context `A_ctx` (e.g., payload specifications, weather data, airspace maps)
> - `E_sys`: system-level defaults and invariant definitions

**Protected Invariants (I_prot)**
> A set of non-negotiable safety constraints that every mission contract must satisfy. These invariants are scenario-independent and encode hard aviation safety rules (e.g., minimum altitude buffers, no-fly zone prohibitions, maximum payload weight limits).

Structure:
```
I_prot = { i_1, i_2, ..., i_n }  where each i_k is an invariant predicate
```

**Proof Obligations (PO)**
> Formal verification conditions derived from the MAC that must be discharged for a mission to be admitted. Five categories exist:

| Obligation | Symbol | Description |
|---|---|---|
| Evidence Proof Obligation | `PO_E` | Every hard clause must have sufficient evidence support (`semantic_support == Y`) |
| Authority Proof Obligation | `PO_A` | Every hard clause must have a valid authority source (`authority != null`) |
| Mutability Proof Obligation | `PO_M` | No hard clause may depend on mutable facts without explicit temporal bounds |
| Uniqueness Proof Obligation | `PO_U` | No two clauses in the contract may be semantically contradictory |
| Boundary Proof Obligation | `PO_B` | The contract must not violate any invariant in `I_prot` |

Each `PO_X` evaluates to `SATISFIED`, `VIOLATED`, or `UNKNOWN`.

**Consequence Signature χ(C)**
> A numerical vector that quantifies the expected mission outcome across seven dimensions if the contract were to be executed. Computed after proof obligation evaluation.

```
χ(C) = {
  executability:           float in [0, 1],
  airspace_compliance:     float in [0, 1],
  communication_feasibility: float in [0, 1],
  payload_satisfaction:    float in [0, 1],
  weather_satisfaction:    float in [0, 1],
  min_energy_margin:       float in [0, 1],
  min_time_margin:         float in [0, 1]
}
```

### 2.2 Ground Truth Labels

| Label | Value | Description |
|---|---|---|
| **ACCEPT** | `"accept"` | All proof obligations satisfied; mission is safe to execute under stated constraints |
| **CLARIFY** | `"clarify"` | At least one proof obligation is `UNKNOWN` or a `Claim_H` is present in hard obligations; requires human operator clarification |
| **REJECT** | `"reject"` | At least one proof obligation is `VIOLATED`; mission cannot be safely executed |

### 2.3 Risk Categories (T1--T6)

| Category | Code | Description | Typical PO Failure |
|---|---|---|---|
| **T1** | `risk_insufficient_evidence` | Evidence base does not support mission requirements | `PO_E` |
| **T2** | `risk_authority_gap` | Clause lacks proper authority or authorization chain | `PO_A` |
| **T3** | `risk_mutability_unbounded` | Mission depends on time-varying conditions without bounds | `PO_M` |
| **T4** | `risk_internal_contradiction` | Clauses within the contract are mutually inconsistent | `PO_U` |
| **T5** | `risk_invariant_violation` | Contract violates protected invariants | `PO_B` |
| **T6** | `risk_compound_failure` | Multiple risk categories present simultaneously | Multiple POs |

### 2.4 Scenarios (S1--S6)

| Scenario | Code | Domain | Context Characteristics |
|---|---|---|---|
| **S1** | `urban_surveillance` | Urban area monitoring | Dense no-fly zones, altitude restrictions |
| **S2** | `rural_inspection` | Agricultural / infrastructure inspection | Open airspace, weather variability |
| **S3** | `search_rescue` | Emergency response | Time-critical, uncertain terrain |
| **S4** | `cargo_delivery` | Package transport | Payload constraints, landing zone requirements |
| **S5** | `environmental_monitoring` | Environmental data collection | Sensor requirements, extended endurance |
| **S6** | `disaster_assessment` | Post-disaster evaluation | Dynamic hazards, degraded communication |

### 2.5 Language Complexity Types

| Type | Description | Example Pattern |
|---|---|---|
| **explicit** | Requirements stated clearly with specific values | `"Fly at 120m altitude with 4K camera"` |
| **semi-structured** | Requirements partially specified, some inference needed | `"Use the best available camera for aerial photography"` |
| **ambiguous** | Requirements vague or open to multiple interpretations | `"Get good footage of the area"` |

### 2.6 Clause Fields

| Field | Type | Description |
|---|---|---|
| `clause.text` | `str` | Natural language content of the clause |
| `clause.mode` | `"hard" \| "soft" \| "pending"` | Obligation strength |
| `clause.type` | `str` | Clause family (e.g., `altitude_constraint`, `payload_requirement`) |
| `clause.semantic_support` | `"Y" \| "N" \| "U"` | Evidence sufficiency (Yes / No / Unknown) |
| `clause.source` | `str` | Origin: `user_explicit`, `context_inferred`, `system_default`, `llm_derived` |
| `clause.authority` | `str \| null` | Authorizing entity or document reference |
| `clause.mutability` | `"fixed" \| "variable" \| "unknown"` | Stability of underlying fact |
| `clause.trust` | `float in [0, 1]` | Confidence score assigned by annotator |
| `clause.evidence_ptr` | `str[]` | Pointers to evidence base entries |

---

## 3. Dual-Agent Annotation Flow

The annotation pipeline proceeds through three strictly sequential stages. No stage may be skipped or reordered.

### 3.1 Stage 1: Agent A --- Construction + Initial Annotation

**Inputs received by Agent A:**

```
Input_A = {
  x:               str,           // raw natural language instruction
  A_ctx:           Context,       // scenario-specific context facts
  I_prot:          Invariant[],   // protected invariants
  E:               EvidenceBase,  // full evidence base
  Γ:               Governance,    // governance parameters and thresholds
  agent_id:        "A"
}
```

**Step-by-step procedure:**

#### Step 1.1: Extract Requirement Anchors

Agent A parses the raw instruction `x` and identifies all explicit and implicit requirement mentions. Each identified requirement becomes a candidate anchor for clause generation.

- Tokenize and segment `x` into requirement-bearing phrases
- Tag each phrase with: requirement_type, explicitness_level, confidence_score
- Record all anchors in `audit_trail.requirement_anchors`

#### Step 1.2: Generate Candidate Contract Clauses

For each requirement anchor, Agent A generates one or more candidate `Clause` objects:

```python
for anchor in requirement_anchors:
    clauses = generate_clauses(anchor, A_ctx, E_sys)
    for clause in clauses:
        candidate_clauses.append(clause)
```

Each candidate clause must include all mandatory fields listed in Section 2.6.

#### Step 1.3: Assign Evidence, Source, Authority, Mutability, and Trust Labels

For each candidate clause:

1. **Source assignment**: Determine origin:
   - If clause text literally matches `x` → `source = "user_explicit"`
   - If derivable from `A_ctx` → `source = "context_inferred"`
   - If matches a system default → `source = "system_default"`
   - If generated by the LLM without direct grounding → `source = "llm_derived"`

2. **Evidence pointer assignment**: Populate `evidence_ptr` with references to supporting entries in `E`.

3. **Authority assignment**: Set `authority` based on the authorizing entity (e.g., `"CAAC_Reg_92"`, `"operator_manual_v3"`, `null` if none).

4. **Mutability assignment**: Classify as `fixed`, `variable`, or `unknown` based on whether the underlying fact can change during mission execution.

5. **Trust score**: Assign a confidence value in `[0, 1]` reflecting annotator certainty.

#### Step 1.4: Compute Proof Obligation Results

Evaluate each of the five proof obligations against the assembled contract:

```
PO_E = check_evidence_sufficiency(all_clauses)
PO_A = check_authority_validity(all_clauses)
PO_M = check_mutability_bounds(all_clauses)
PO_U = check_internal_consistency(all_clauses)
PO_B = check_invariant_compliance(all_clauses, I_prot)
```

Each PO returns one of: `SATISFIED`, `VIOLATED`, `UNKNOWN`.

#### Step 1.5: Compute Consequence Signature χ(C)

Using the governance function `Γ.compute_signature(PO_results, clauses, A_ctx)`:

```
χ(C) = Γ.compute_signature(PO_E, PO_A, PO_M, PO_U, PO_B, clauses, A_ctx)
```

The result is a 7-dimensional vector as defined in Section 2.1.

#### Step 1.6: Produce Initial Admission Decision

Map PO results to admission label using the decision function:

```
if any(PO == VIOLATED for PO in [PO_E, PO_A, PO_M, PO_U, PO_B]):
    decision = REJECT
elif any(PO == UNKNOWN for PO in [PO_E, PO_A, PO_M, PO_U, PO_B]):
    decision = CLARIFY
else:
    decision = ACCEPT
```

#### Step 1.7: Assign Risk Category

Map the failed proof obligation(s) to risk category:

```
if multiple POs failed:
    risk_category = T6
else:
    risk_category = map_po_to_risk(failed_po)  // T1--T5
```

#### Step 1.8: Record Full Audit Trail

Agent A writes a complete `AuditEntry` for every significant decision:

```
AuditEntry = {
  timestamp: ISO8601,
  step: str,           // which annotation step
  input: any,          // input to the decision
  output: any,         // output of the decision
  reasoning: str,      // natural language rationale
  confidence: float    // agent confidence in [0, 1]
}
```

**Output of Stage 1:** `MAC_A` --- the complete mission admission contract annotated by Agent A.

### 3.2 Stage 2: Agent B --- Independent Review

**Critical isolation requirement:** Agent B receives **identical raw inputs** as Agent A (`x`, `A_ctx`, `I_prot`, `E`, `Γ`) but **does NOT** receive any output from Agent A. This isolation is mandatory and must be enforced by the pipeline infrastructure.

```
Input_B = {
  x:               str,           // same raw instruction
  A_ctx:           Context,       // same scenario context
  I_prot:          Invariant[],   // same invariants
  E:               EvidenceBase,  // same evidence base
  Γ:               Governance,    // same governance
  agent_id:        "B"
  // NO mac_A, NO audit_trail_A, NO intermediate outputs from A
}
```

Agent B performs **exactly the same 7 steps** as Agent A (Steps 1.1--1.7) and produces `MAC_B` with its own independent `audit_trail_B`.

**No information may flow from Stage 1 to Stage 2.**

### 3.3 Stage 3: Intersection Arbitration

After both agents complete their independent annotations, the arbitration module compares `MAC_A` and `MAC_B` field by field.

**Comparison fields:**

```
Fields compared:
  1. admission_decision   (ACCEPT / CLARIFY / REJECT)
  2. risk_category        (T1--T6)
  3. clauses[]            (core fields + non-core fields)
  4. consequence_signature χ(C)   (7-dimensional vector)
```

For each field, apply the arbitration rules defined in Section 4. Record all outcomes in `arbitration_notes`.

**Output of Stage 3:**

```
ArbitrationResult = {
  mac_arbitrated: MAC,         // the resolved contract
  status: "APPROVED" | "CONFLICT" | "PARTIAL_CONFLICT" | "NUMERICAL_CONFLICT",
  conflicts: Conflict[],       // list of all detected conflicts
  resolution: str,             // how conflicts were resolved
  escalation_level: int,       // 1--4 per Section 8
  arbitration_notes: str,      // human-readable summary
  resolved_by: "auto" | "manual" | "panel"
}
```

---

## 4. Intersection Arbitration Rules

All comparisons between `MAC_A` and `MAC_B` follow the four rules below. Rules are evaluated in order; if any rule triggers a conflict, subsequent rules may still be evaluated for diagnostic purposes but the sample is already marked for escalation.

### 4.1 Rule 1: Admission Label Agreement

**Statement:** `MAC_A.admission_decision` and `MAC_B.admission_decision` must be identical.

```
if MAC_A.decision == MAC_B.decision:
    status = "AGREE"
else:
    status = "CONFLICT"
    route_to = "manual_arbitration"
```

| Condition | Outcome | Action |
|---|---|---|
| A = B (all three match) | `AGREE` | Continue to Rule 2 |
| A != B (any mismatch) | `CONFLICT` | Route to manual arbitration; human expert makes final decision and records reasoning |

**Example:**
```
MAC_A.decision = ACCEPT
MAC_B.decision = CLARIFY
→ CONFLICT → manual arbitration
```

### 4.2 Rule 2: Risk Category Agreement

**Statement:** `MAC_A.risk_category` and `MAC_B.risk_category` must be identical.

**Rationale:** The risk category determines which proof obligation(s) failed. Disagreement at this level indicates fundamental disagreement about *why* a mission is problematic, which must be resolved before the sample can enter the ground-truth corpus.

```
if MAC_A.risk_category == MAC_B.risk_category:
    status = "AGREE"
else:
    status = "CONFLICT"
    route_to = "manual_arbitration"
```

| Condition | Outcome | Action |
|---|---|---|
| A.risk == B.risk | `AGREE` | Continue to Rule 3 |
| A.risk != B.risk | `CONFLICT` | Route to manual arbitration |

**Example:**
```
MAC_A.risk_category = T1   // insufficient evidence
MAC_B.risk_category = T3   // mutability unbounded
→ CONFLICT → manual arbitration
```

### 4.3 Rule 3: Clause Mode Agreement

#### 4.3.1 Field Classification

Clause fields are divided into **core fields** and **non-core fields**:

**Core fields** (must agree between agents):

| Field | Type | Agreement Criterion |
|---|---|---|
| `clause.mode` | `"hard" \| "soft" \| "pending"` | Exact string match |
| `clause.type` | `str` | Exact string match |
| `clause.semantic_support` | `"Y" \| "N" \| "U"` | Exact string match |

**Non-core fields** (differences allowed but logged):

| Field | Type | Disposition |
|---|---|---|
| `clause.authority` | `str \| null` | Log discrepancy, do not block |
| `clause.mutability` | `"fixed" \| "variable" \| "unknown"` | Log discrepancy, do not block |
| `clause.trust` | `float in [0, 1]` | Log discrepancy, do not block |

#### 4.3.2 Agreement Procedure

For each clause pair (matched by `clause.text` or `clause.id`):

```
for each matched_clause_pair (c_A, c_B):
    for each core_field in [mode, type, semantic_support]:
        if c_A[core_field] != c_B[core_field]:
            mark PARTIAL_CONFLICT
            record_conflict(clause_id, core_field, c_A[core_field], c_B[core_field])
```

| Condition | Outcome | Action |
|---|---|---|
| All core fields agree on all clauses | `AGREE` | Continue to Rule 4 |
| Any core field differs on any clause | `PARTIAL_CONFLICT` | Route to review; senior annotator adjudicates |

Non-core field differences are recorded in the `discrepancy_log` but **do not block approval**.

**Example:**
```
Clause X:
  A.mode = "hard",      B.mode = "soft"       → PARTIAL_CONFLICT
  A.type = "altitude",  B.type = "altitude"   → AGREE
  A.support = "Y",      B.support = "Y"       → AGREE
  A.authority = "CAAC", B.authority = null    → logged discrepancy only
```

### 4.4 Rule 4: Consequence Signature Agreement

**Statement:** Each dimension of `χ(C)_A` and `χ(C)_B` must agree within specified tolerances.

#### 4.4.1 Tolerance Definitions

For **dimension fields** (`executability`, `airspace_compliance`, `communication_feasibility`, `payload_satisfaction`, `weather_satisfaction`):

```
agree if |χ_A.dim - χ_B.dim| / max(χ_A.dim, χ_B.dim, ε) ≤ 0.10
```

where `ε = 1e-6` prevents division by zero.

For **margin fields** (`min_energy_margin`, `min_time_margin`):

```
agree if |χ_A.margin - χ_B.margin| ≤ 0.10 * max(χ_A.margin, χ_B.margin, ε)
```

#### 4.4.2 Agreement Procedure

```
for dim in χ.dimensions:
    if within_tolerance(χ_A[dim], χ_B[dim]):
        mark "AGREE"
    else:
        mark "NUMERICAL_CONFLICT"
        record_conflict("consequence_signature", dim, χ_A[dim], χ_B[dim])
```

| Condition | Outcome | Action |
|---|---|---|
| All 7 dimensions within tolerance | `AGREE` | Sample approved at this rule |
| Any dimension exceeds tolerance | `NUMERICAL_CONFLICT` | Route to review |

**Example:**
```
Dimension: executability
  χ_A = 0.85, χ_B = 0.80
  relative_diff = |0.85 - 0.80| / 0.85 = 0.059 → within 10% → AGREE

Dimension: min_energy_margin
  χ_A = 0.30, χ_B = 0.15
  abs_diff = 0.15; tolerance = 0.10 * 0.30 = 0.03
  0.15 > 0.03 → NUMERICAL_CONFLICT
```

---

## 5. Claim_H (LLM Hypothesis) Identification Rules

A `Claim_H` is an unverified hypothesis introduced by the LLM during clause generation that is not grounded in the original instruction, context, or system defaults. All `Claim_H` instances must be flagged and handled per the rules below.

### 5.1 Keyword Blacklist Method

#### 5.1.1 Blacklisted Keywords

**Chinese keywords** indicating assumption or speculation:

```
[ "假设", "推测", "可能", "估计", "大概", "或许", "似乎", "应该" ]
```

**English keywords** indicating assumption or speculation:

```
[ "assume", "assume that", "presumably", "probably", "might",
  "could be", "estimate", "suppose", "hypothetically" ]
```

#### 5.1.2 Flagging Procedure

```
for clause in MAC.clauses:
    if any(keyword in clause.text.lower() for keyword in blacklist):
        flag_claim_h(clause.id, reason="keyword_match", matched_keyword=keyword)
```

**Important:** A keyword match **does not** automatically mean the clause is rejected. It means the clause **must undergo mandatory evidence checking** per Section 5.2.

### 5.2 Context Evidence Absence Method

#### 5.2.1 Four-Condition Test

A clause is flagged as `Claim_H` if **all** of the following conditions hold simultaneously:

| # | Condition | Verification Method |
|---|---|---|
| C1 | Clause text cannot be literally matched to any text anchor in original instruction `x` | Normalized string matching against `x` (threshold < 0.80) |
| C2 | Clause content cannot be derived from context facts in `A_ctx` via documented inference rules | Check `A_ctx` key-value pairs and inference rule catalog |
| C3 | Clause content is not a system default | Cross-reference against `evidence_base.system_defaults` |
| C4 | Clause was introduced during LLM clause generation (`source == "llm_derived"`) | Check `clause.source` field |

```
is_claim_h = (C1 AND C2 AND C3 AND C4)
```

#### 5.2.2 Decision Flowchart

```
if clause.source == "user_explicit":
    → NOT Claim_H (end)

elif clause.source == "context_inferred":
    if evidence_exists(clause.evidence_ptr):
        → NOT Claim_H (end)
    else:
        → CHECK evidence_ptr → if insufficient → FLAG Claim_H

elif clause.source == "system_default":
    if matches_system_default(clause):
        → NOT Claim_H (end)
    else:
        → FLAG Claim_H

elif clause.source == "llm_derived":
    → CHECK clause.evidence_ptr
    → if evidence_ptr is empty:
        → FLAG Claim_H
    → elif evidence_ptr points to insufficient evidence:
        → FLAG Claim_H
    → elif evidence_ptr points to sufficient evidence:
        → NOT Claim_H (end)
```

#### 5.2.3 Example

```
Instruction x: "Fly over the corn field and take photos."

Clause: "The corn field is located at GPS coordinates (39.9042, 116.4074)."
  source = "llm_derived"
  evidence_ptr = []  // empty
  C1: text not in x → TRUE
  C2: no context fact supports this → TRUE
  C3: not a system default → TRUE
  C4: source == "llm_derived" → TRUE
  → FLAG Claim_H: llm_invented_coordinates
```

### 5.3 Escalation Rules

#### 5.3.1 Audit Trail Requirement

Every `Claim_H` flag must produce an audit entry:

```
Claim_H_AuditEntry = {
  timestamp: ISO8601,
  clause_id: str,
  flag_reason: "keyword_match" | "evidence_absence" | "both",
  conditions_met: {C1: bool, C2: bool, C3: bool, C4: bool},
  resolution: str,        // how the flag was resolved
  escalated: bool         // whether escalation occurred
}
```

#### 5.3.2 Hard Obligation Rule

If a flagged `Claim_H` clause has `mode == "hard"`:

```
if Claim_H in hard_obligations:
    if decision was ACCEPT:
        → OVERRIDE to CLARIFY or REJECT (annotator discretion)
    mandatory_note = "Claim_H detected in hard obligation; decision elevated"
```

This is an **automatic escalation** --- no annotator may override this rule without panel review.

#### 5.3.3 Pending Set Rule

If a flagged `Claim_H` clause has `mode == "pending"`:

```
if Claim_H in pending_set:
    → Acceptable; record for future review
    → Include in sample metadata: "pending_claims_present: true"
```

---

## 6. Evidence Support Determination

### 6.1 Text Anchor Matching

#### 6.1.1 Normalization Pipeline

Before matching, apply the following normalization:

```
normalize(text):
    1. Convert to lowercase
    2. Remove punctuation: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    3. Strip leading and trailing whitespace
    4. Collapse multiple whitespace characters to single space
    5. (Chinese text only) maintain character segmentation
```

#### 6.1.2 Match Thresholds

Let `match_ratio = |normalized_clause ∩ normalized_instruction| / |normalized_clause|`:

| Match Ratio | `semantic_support` | Meaning |
|---|---|---|
| `≥ 0.80` | `Y` | Supported --- clause is grounded in instruction text |
| `0.50 -- 0.80` | `U` | Insufficient --- partial match, needs clarification |
| `< 0.50` | `N` | Unsupported --- clause not grounded in instruction |

**Example:**
```
Clause: "fly altitude minimum 50 meters"
Instruction: "fly at least fifty meters above ground"

Normalized clause: "fly altitude minimum 50 meters"
Normalized instruction: "fly at least fifty meters above ground"

Match ratio = 2/6 ≈ 0.33 → semantic_support = N
```

### 6.2 Context Fact Matching

A clause is **context-supported** if its semantic content can be verified against entries in `A_ctx`.

#### 6.2.1 Key-Value Overlap Method

```
for fact in A_ctx:
    if field_agreement(clause.parameters, fact.parameters) >= 0.80:
        → context_supported = true
        → add fact.id to clause.evidence_ptr
```

**Example:**
```
Clause: "Use camera resolution of 4K for aerial survey"
Context fact: { "payload.camera.max_resolution": "4K", "payload.camera.type": "EO/IR" }

Field agreement: clause requires 4K, context confirms 4K available
→ context_supported = true
→ evidence_ptr += ["ctx.payload.camera.max_resolution"]
```

### 6.3 Composite Evidence

Some clauses require **multiple evidence sources** for full support.

#### 6.3.1 Composite Evaluation Rules

```
semantic_support = Y  if ALL required evidence sources match
semantic_support = U  if ANY required evidence source is missing
semantic_support = N  if ANY required evidence source contradicts the clause
```

#### 6.3.2 Recording Composite Evidence

```
clause.evidence_ptr = [
    "E_user:anchor_3",           // user instruction anchor
    "E_ctx:payload.camera",      // context fact
    "E_ctx:weather.visibility",  // context fact
    "E_sys:default_altitude"     // system default
]
```

Each pointer must be validated individually. The overall `semantic_support` is determined by the composite rules above.

### 6.4 Evidence Mismatch Resolution

#### 6.4.1 Priority Rule

If `evidence_base` and `A_ctx` provide contradictory information:

```
if E_user contradicts E_ctx:
    → A_ctx takes priority as ground truth
    → Record discrepancy in audit trail
    → Flag sample for quality review with note: "evidence_mismatch_user_vs_context"

if E_sys contradicts E_ctx:
    → A_ctx takes priority
    → Record discrepancy
    → Flag for review
```

**Rationale:** `A_ctx` contains scenario-specific verified data (e.g., actual weather readings, verified payload specs). User instructions may contain errors or outdated information. System defaults are fallbacks and may not reflect the specific mission context.

#### 6.4.2 Mismatch Audit Entry

```
MismatchAuditEntry = {
  timestamp: ISO8601,
  discrepancy_type: "user_vs_context" | "system_vs_context" | "user_vs_system",
  field: str,                  // which field conflicted
  value_user: any,             // value from user instruction
  value_context: any,          // value from context
  value_system: any,           // value from system defaults
  resolution: str,             // which source was chosen
  reason: str                  // rationale for resolution
}
```

---

## 7. Annotation Quality Checklist

Every annotated sample must pass the following checklist before being admitted to the EAMSR-Bench ground-truth corpus. Check each box and record the outcome.

### 7.1 Pre-Arbitration Checks

- [ ] **Agent A completed independently** --- `MAC_A` is fully populated with all required fields
- [ ] **Agent B completed independently** --- `MAC_B` is fully populated with all required fields
- [ ] **No information leakage** --- Agent B's audit trail confirms no access to Agent A outputs
- [ ] **Agent isolation verified** --- Pipeline logs confirm independent execution environments

### 7.2 Arbitration Checks

- [ ] **Admission labels agree** --- `MAC_A.decision == MAC_B.decision`, OR conflict routed to manual arbitration with resolution
- [ ] **Risk categories agree** --- `MAC_A.risk_category == MAC_B.risk_category`, OR conflict routed to manual arbitration with resolution
- [ ] **Core clause fields agree** --- All `[mode, type, semantic_support]` match across matched clause pairs, OR `PARTIAL_CONFLICT` resolved
- [ ] **Consequence signatures within tolerance** --- All 7 dimensions within ±10%, OR `NUMERICAL_CONFLICT` resolved

### 7.3 Claim_H Checks

- [ ] **No Claim_H in hard obligations** --- No hard-mode clause has an active `Claim_H` flag (unless explicitly overridden by panel)
- [ ] **All Claim_H flags documented** --- Every `Claim_H` flag has a complete `Claim_H_AuditEntry`
- [ ] **Pending Claim_H acceptable** --- Any `Claim_H` in `pending_set` is noted in sample metadata

### 7.4 Evidence and Audit Checks

- [ ] **Evidence pointers complete** --- Every non-default clause has at least one entry in `evidence_ptr`
- [ ] **Evidence mismatch resolved** --- Any `E_user` vs `E_ctx` discrepancies are recorded and resolved
- [ ] **Audit trail complete (Agent A)** --- All 7 annotation steps have `AuditEntry` records
- [ ] **Audit trail complete (Agent B)** --- All 7 annotation steps have `AuditEntry` records
- [ ] **Arbitration notes recorded** --- All conflicts, resolutions, and escalation decisions documented

### 7.5 Final Approval

- [ ] **Escalation level assigned** --- Level 1--4 per Section 8
- [ ] **Final reviewer signature** --- Human reviewer ID and timestamp recorded
- [ ] **Sample committed** --- Sample hash recorded and verified

---

## 8. Conflict Resolution Escalation

The escalation hierarchy defines how disagreements between Agent A and Agent B are resolved. Each level has clear entry criteria and resolution authority.

### 8.1 Escalation Levels

#### Level 1: Automatic Agreement

| Criterion | `MAC_A` and `MAC_B` are identical on all compared fields |
|---|---|
| **Authority** | Automatic --- no human review required |
| **Resolution** | Sample approved; both agents' outputs are cross-validated |
| **Action** | Commit sample to ground-truth corpus; record approval timestamp |

```
if (A.decision == B.decision) AND
   (A.risk == B.risk) AND
   (all_core_fields_agree) AND
   (all_signature_dims_within_tolerance):
    → LEVEL 1 → APPROVED
```

#### Level 2: Non-Core Field Differences Only

| Criterion | Core fields agree; only non-core fields (`authority`, `mutability`, `trust`) differ |
|---|---|
| **Authority** | Automatic with discrepancy logging |
| **Resolution** | Sample approved; non-core differences recorded in `discrepancy_log` |
| **Action** | Use Agent A's values as primary; log Agent B's values as alternative |

```
if (LEVEL_1_conditions.core == true) AND
   (any_non_core_field_differs):
    → LEVEL 2 → APPROVED with discrepancy_log
```

#### Level 3: Core Field or Label Conflicts

| Criterion | Any core field differs, OR admission labels differ, OR risk categories differ |
|---|---|
| **Authority** | Senior annotator (human expert with ≥ 50 hours EAMSR annotation experience) |
| **Resolution** | Senior annotator reviews both MACs, audit trails, and raw inputs; makes binding decision |
| **Action** | Senior annotator produces `ResolutionNote` with full rationale; decision is final unless Level 4 triggered |

```
if (admission_labels_differ) OR
   (risk_categories_differ) OR
   (any_core_field_differs) OR
   (any_signature_dim_exceeds_tolerance):
    → LEVEL 3 → SENIOR_ANNOTATOR_REVIEW
```

**Senior annotator procedure:**
1. Read both `MAC_A` and `MAC_B` in full
2. Review both `audit_trail_A` and `audit_trail_B`
3. Re-examine the raw instruction `x` and context `A_ctx`
4. Evaluate proof obligations independently if needed
5. Produce final `MAC_final` with complete `ResolutionNote`

#### Level 4: Expert Panel Review

| Criterion | Senior annotator is uncertain, OR the sample involves novel scenario interpretation, OR Level 3 produced an anomalous result |
|---|---|
| **Authority** | Panel of 3+ domain experts (UAV operations, aviation law, NLP) |
| **Resolution** | Majority vote among panel members; written consensus document required |
| **Action** | Panel produces `PanelResolution` document; sample held in review queue until resolved |

```
if (senior_annotator.uncertain == true) OR
   (sample_flags.include("novel_scenario")) OR
   (level_3_result.anomalous == true):
    → LEVEL 4 → EXPERT_PANEL_REVIEW
```

**Panel procedure:**
1. Each panel member independently reviews the case
2. Panel convenes (synchronous or asynchronous) to discuss
3. Each member casts a vote for the final `MAC`
4. Majority wins; ties broken by senior aviation safety expert
5. `PanelResolution` document is archived with the sample

### 8.2 Escalation Summary Table

| Level | Trigger | Authority | Outcome | Human Effort |
|---|---|---|---|---|
| 1 | Full agreement (all fields) | Automatic | Approved | None |
| 2 | Non-core field differences only | Automatic + log | Approved with log | None |
| 3 | Core field or label conflicts | Senior annotator | Binding decision | ~15 min/sample |
| 4 | Senior uncertain or novel | Expert panel (3+) | Consensus decision | ~60 min/sample |

### 8.3 Escalation Routing Diagram

```
┌─────────────────┐
│  A and B submit │
│     MACs        │
└────────┬────────┘
         ▼
┌──────────────────────────────────────┐
│  Compare all fields (Rules 1--4)     │
└────────┬─────────────────────┬───────┘
         │                     │
    All agree             Any conflict
         │                     │
         ▼                     ▼
┌─────────────┐       ┌──────────────────┐
│   Level 1   │       │ Identify conflict│
│  APPROVED   │       │     type         │
└─────────────┘       └────────┬─────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Non-core diff    Core/label diff   Senior unsure
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │  Level 2 │    │  Level 3 │    │  Level 4 │
        │ APPROVED │    │  Senior  │    │  Panel   │
        │  + log   │    │ Annotator│    │  (3+)    │
        └──────────┘    └──────────┘    └──────────┘
```

---

## Appendix A: Sample Annotation Record Template

```json
{
  "sample_id": "EAMSR_001_S1_explicit",
  "contract_id": "MAC_20260615_001",
  "scenario": "S1",
  "language_type": "explicit",
  "raw_instruction": "...",
  "mac_a": { /* full MAC from Agent A */ },
  "mac_b": { /* full MAC from Agent B */ },
  "arbitration_result": {
    "status": "APPROVED",
    "escalation_level": 1,
    "conflicts": [],
    "resolved_by": "auto",
    "arbitration_notes": "Full agreement between agents."
  },
  "quality_checklist": {
    "pre_arbitration": { "all_passed": true },
    "arbitration": { "all_passed": true },
    "claim_h": { "all_passed": true },
    "evidence_audit": { "all_passed": true },
    "final_approval": { "approved": true, "reviewer": "auto", "timestamp": "..." }
  },
  "committed_to_corpus": true,
  "commit_hash": "sha256:..."
}
```

## Appendix B: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-06-15 | EAMSR Team | Initial protocol definition |

---

*End of Document --- EAMSR Annotation Protocol v1.0*
