"""
EAMSR JSON Schema Validation Module
====================================

This module provides JSON Schema (Draft 7) definitions and Python validation
utilities for the **Evidence-carrying Autonomous Mission Safety & Reasoning
(EAMSR)** experimental framework.

EAMSR converts natural-language UAV mission instructions into structured
**Mission Admission Contracts (MAC)** and validates them through a 5-stage
pipeline.  The experimental framework evaluates the system on 120 tasks across
6 scenarios, 6 risk categories, and 3 language types.

Document references
-------------------
* Method document — Section 3: MAC pipeline (5 stages)
* Method document — Section 3.1: Inputs (x, A_ctx, I_prot, E, Gamma)
* Method document — Section 3.2: Candidate MAC generation
* Method document — Section 3.3: Governance & relaxation
* Method document — Section 3.4: Proof obligations (PO_E … PO_B)
* Method document — Section 3.5: Consequence signature & decision
* Experiment document — Section 4: Experimental design (120 tasks, 6 scenarios,
  6 risk tiers, 3 language types, 11 methods)

Schemas defined
---------------
1. **MissionSample** — a single experimental task (NL instruction + context +
   evidence + governance + ground-truth annotations).
2. **MAC** — Mission Admission Contract produced by the pipeline (clauses +
   proof obligations + consequence signature + decision).
3. **ExperimentResult** — outcome of running one method on one sample
   (decision, metrics, witness plan, budget).

The module exposes three validation helpers and a ``get_schema`` factory::

    from eamsr_schemas import (
        validate_mission_sample,
        validate_mac,
        validate_experiment_result,
        get_schema,
    )

    # Validate a raw dict against a schema
    validate_mission_sample(my_dict)   # raises jsonschema.ValidationError on failure

    # Retrieve the JSON Schema dict for external use
    schema = get_schema("MissionSample")

Dependencies
------------
* ``jsonschema`` (for validation)
* Python 3.7+ (dataclasses, typing)

"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

# ---------------------------------------------------------------------------
# Optional jsonschema import with graceful degradation
# ---------------------------------------------------------------------------
try:
    from jsonschema import Draft7Validator, ValidationError, validate as _jsonschema_validate

    _HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    _HAS_JSONSCHEMA = False
    Draft7Validator = None  # type: ignore[misc,assignment]
    ValidationError = Exception  # type: ignore[misc,assignment]
    _jsonschema_validate = None  # type: ignore[misc,assignment]

# ---------------------------------------------------------------------------
# Constants — enumerated values shared across schemas
# ---------------------------------------------------------------------------

SCENARIOS: Tuple[str, ...] = (
    "S1_Powerline",
    "S2_Disaster_area",
    "S3_Campus_delivery",
    "S4_River_monitoring",
    "S5_Bridge_inspection",
    "S6_Communication_limited",
)

RISK_CATEGORIES: Tuple[str, ...] = (
    "T1_Normal",
    "T2_Evidence_insufficient",
    "T3_Authority_conflicting",
    "T4_LLM_assumption",
    "T5_Backend_infeasible",
    "T6_Consequence_ambiguous",
)

LANGUAGE_TYPES: Tuple[str, ...] = ("explicit", "semi_structured", "ambiguous")

CLAUSE_TYPES: Tuple[str, ...] = (
    "objective",
    "spatial",
    "temporal",
    "energy",
    "payload",
    "communication",
    "contingency",
    "preference",
)

CLAUSE_MODES: Tuple[str, ...] = ("hard", "soft", "optional", "default", "pending")

CLAUSE_SOURCES: Tuple[str, ...] = (
    "user_explicit",
    "user_implied",
    "llm_derived",
    "system_default",
    "context_inferred",
)

MUTABILITIES: Tuple[str, ...] = ("keep", "weaken", "drop", "default", "clarify")

TRUST_LEVELS: Tuple[str, ...] = ("trusted", "untrusted", "verified")

SEMANTIC_SUPPORTS: Tuple[str, ...] = ("Y", "N", "U")

DECISIONS: Tuple[str, ...] = ("ACCEPT", "CLARIFY", "REJECT")

METHODS: Tuple[str, ...] = (
    "Direct_LLM",
    "LLM_Backend",
    "Rule_Gate",
    "Greedy_Relaxation",
    "Full_EAMSR",
    "Ablation_No_Evidence",
    "Ablation_No_Authority_Mutability",
    "Ablation_No_USI",
    "Ablation_No_MCS",
    "Ablation_No_Backend_Witness",
    "Ablation_No_Audit_Trail",
)

# ---------------------------------------------------------------------------
# Regex patterns for identifier validation
# ---------------------------------------------------------------------------

RE_SAMPLE_ID = re.compile(
    r"^MS-S[1-6]-T[1-6]-(explicit|semi_structured|ambiguous)-\d{2}$"
)
RE_CONTRACT_ID = re.compile(
    r"^MAC-MS-S[1-6]-T[1-6]-(explicit|semi_structured|ambiguous)-\d{2}-\d+$"
)
RE_CLAUSE_ID = re.compile(r"^CL-\d+$")
RE_RUN_ID = re.compile(
    r"^RUN-(Direct_LLM|LLM_Backend|Rule_Gate|Greedy_Relaxation|Full_EAMSR|"
    r"Ablation_No_Evidence|Ablation_No_Authority_Mutability|Ablation_No_USI|"
    r"Ablation_No_MCS|Ablation_No_Backend_Witness|Ablation_No_Audit_Trail)-"
    r"MS-S[1-6]-T[1-6]-(explicit|semi_structured|ambiguous)-\d{2}-\d+$"
)


# =============================================================================
# Data-class helpers
# =============================================================================

def _as_dict(obj: Any) -> Any:
    """Recursively convert a dataclass instance to a dict.

    Parameters
    ----------
    obj:
        A dataclass instance, list, dict, or primitive value.

    Returns
    -------
    Any
        A JSON-serialisable representation of *obj*.
    """
    from dataclasses import asdict, is_dataclass

    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _as_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_as_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _as_dict(v) for k, v in obj.items()}
    return obj


# =============================================================================
# Schema 1 — MissionSample
# =============================================================================

@dataclass
class GeoPoint:
    """Geographic coordinate."""

    lat: float
    lon: float


@dataclass
class TimeWindow:
    """A time window with ISO-8601 start and end timestamps."""

    start: str
    end: str


@dataclass
class InitialState:
    """UAV initial state at mission start."""

    position: GeoPoint
    battery_wh: float
    altitude_m: float


@dataclass
class Weather:
    """Weather conditions."""

    condition: str
    wind_speed_ms: float
    visibility_m: float
    temperature_c: float


@dataclass
class Environment:
    """Operational environment snapshot."""

    weather: Weather
    terrain: str
    date_time: str


@dataclass
class CommunicationMap:
    """Communication coverage map."""

    coverage_areas: List[List[List[List[float]]]]
    bandwidth_mbps: float
    blackout_zones: List[List[List[List[float]]]] = field(default_factory=list)


@dataclass
class PayloadStatus:
    """Available UAV payload / sensors."""

    available_sensors: List[str]
    max_capacity_kg: float
    current_load_kg: float = 0.0


@dataclass
class UAVContext:
    """Trusted UAV context A_ctx (Section 3.1).

    Attributes
    ----------
    uav_model:
        UAV platform model, e.g. ``"quadcopter"``, ``"fixed-wing"``.
    initial_state:
        GPS position, battery energy, and altitude at take-off.
    environment:
        Weather, terrain, and mission date/time.
    communication_map:
        Coverage areas, bandwidth, and blackout zones.
    payload_status:
        Available sensors and payload capacity.
    no_fly_zones:
        Restricted airspace polygons (GeoJSON-style).
    geofence:
        Operational boundary polygon.
    time_windows:
        Allowed operation time windows.
    """

    uav_model: str
    initial_state: InitialState
    environment: Environment
    communication_map: CommunicationMap
    payload_status: PayloadStatus
    no_fly_zones: List[List[List[List[float]]]]
    geofence: List[List[List[float]]]
    time_windows: List[TimeWindow]


@dataclass
class ProtectedInvariants:
    """Protected invariants I_prot that must not be violated (Section 3.1).

    Attributes
    ----------
    return_reserve_wh:
        Minimum energy reserve (Wh) for safe return-to-home.
    max_altitude_m:
        Maximum allowed altitude in metres.
    max_speed_ms:
        Maximum allowed ground speed in m/s.
    payload_max_kg:
        Maximum payload mass in kg.
    emergency_conditions:
        Conditions that trigger emergency abort.
    prohibited_modifications:
        Mission parameters that must not be modified by LLM derivation.
    """

    return_reserve_wh: float
    max_altitude_m: float
    max_speed_ms: float
    payload_max_kg: float
    emergency_conditions: List[str]
    prohibited_modifications: List[str]


@dataclass
class TextAnchor:
    """A text span extracted from the natural-language instruction."""

    anchor_id: str
    text_span: str
    source: str


@dataclass
class ContextFact:
    """A factual assertion derived from the UAV context."""

    fact_id: str
    fact_type: str
    value: Any
    confidence: float


@dataclass
class ProtectedConstraint:
    """A protected constraint that must be preserved."""

    constraint_id: str
    description: str
    type: str


@dataclass
class SystemDefault:
    """A system default rule applied when no explicit instruction is given."""

    default_id: str
    rule: str
    condition: str


@dataclass
class EvidenceBase:
    """Evidence library E (Section 3.1).

    Attributes
    ----------
    text_anchors:
        Anchored text spans from the NL instruction.
    context_facts:
        Verified facts from the UAV context.
    protected_constraints:
        Constraints that must not be violated.
    system_defaults:
        Default rules for missing information.
    """

    text_anchors: List[TextAnchor]
    context_facts: List[ContextFact]
    protected_constraints: List[ProtectedConstraint]
    system_defaults: List[SystemDefault]


@dataclass
class GovernanceStrategy:
    """Governance strategy Gamma (Section 3.3).

    Attributes
    ----------
    source_verification:
        Required evidence sources and their trust levels.
    authority_levels:
        Authority hierarchy (role -> permission level).
    mutability_rules:
        Rules governing how clauses may be transformed.
    """

    source_verification: Dict[str, Any]
    authority_levels: Dict[str, str]
    mutability_rules: List[Dict[str, Any]]


@dataclass
class AgentAnnotation:
    """Annotation from a single agent in the dual-agent annotation protocol."""

    decision: str
    risk_category: str
    clauses: List[str]
    confidence: float
    timestamp: str


@dataclass
class ArbitrationResult:
    """Result of dual-agent arbitration."""

    status: Literal["agreed", "conflict", "manual"]
    final_label: str
    arbitrator: str
    notes: str


@dataclass
class AgreementScores:
    """Per-field inter-annotator agreement rates."""

    decision_agreement: float
    risk_category_agreement: float
    clause_agreement: float
    overall_cohen_kappa: float


@dataclass
class Annotations:
    """Dual-agent annotation results for a MissionSample."""

    agent_a: AgentAnnotation
    agent_b: AgentAnnotation
    arbitration: ArbitrationResult
    agreement_scores: AgreementScores


@dataclass
class MissionSample:
    """A single mission sample in the EAMSR dataset (Section 4).

    Combines a natural-language instruction, trusted UAV context, protected
    invariants, evidence base, governance strategy, ground-truth decision, and
    dual-agent human annotations.

    Attributes
    ----------
    sample_id:
        Unique identifier. Format: ``MS-{scenario}-{risk}-{lang}-{number}``,
        e.g. ``"MS-S1-T1-explicit-01"``.
    scenario:
        One of six UAV mission scenarios.
    risk_category:
        One of six risk taxonomy tiers (T1-T6).
    language_type:
        Natural-language instruction type.
    instruction:
        Raw natural-language task instruction (x).
    context:
        Trusted UAV context A_ctx.
    invariants:
        Protected invariants I_prot.
    evidence_base:
        Evidence library E.
    governance:
        Governance strategy Gamma.
    ground_truth:
        Human-adjudicated ground-truth decision.
    annotations:
        Dual-agent annotation results.
    """

    sample_id: str
    scenario: str
    risk_category: str
    language_type: str
    instruction: str
    context: UAVContext
    invariants: ProtectedInvariants
    evidence_base: EvidenceBase
    governance: GovernanceStrategy
    ground_truth: str
    annotations: Annotations

    def to_dict(self) -> Dict[str, Any]:
        """Serialise this sample to a JSON-compatible dict."""
        return _as_dict(self)  # type: ignore[return-value]


# =============================================================================
# Schema 2 — MAC (Mission Admission Contract)
# =============================================================================

@dataclass
class ClauseFormalSemantic:
    """Structured mission semantics for a clause (location, action, parameters)."""

    location: Dict[str, Any] = field(default_factory=dict)
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)


@dataclass
class MACClause:
    """A single clause in the Mission Admission Contract (Section 3.2).

    Attributes
    ----------
    id:
        Clause identifier, e.g. ``"CL-1"``, ``"CL-2"``.
    anchor:
        Text anchor or context pointer.
    type:
        Clause semantic type.
    mode:
        Contract mode (hard/soft/optional/default/pending).
    source:
        Origin of the clause.
    evidence_ptr:
        References to ``evidence_base`` entries.
    authority:
        Authority level for this clause.
    mutability:
        Governance mutability rule.
    trust:
        Trust assignment.
    semantic_support:
        Evidence support status (Y/N/U).
    formal_semantic:
        Structured mission semantics.
    """

    id: str
    anchor: str
    type: str
    mode: str
    source: str
    evidence_ptr: List[str]
    authority: str
    mutability: str
    trust: str
    semantic_support: str
    formal_semantic: ClauseFormalSemantic


@dataclass
class ProofObligations:
    """Proof obligation results from the 5-stage pipeline (Section 3.4).

    Attributes
    ----------
    PO_E:
        Evidence obligation — all claims grounded in evidence?
    PO_A:
        Authority obligation — conflicting authorities resolved?
    PO_M:
        Mutability obligation — only allowed transformations applied?
    PO_U:
        Untrusted semantic isolation obligation — untrusted clauses isolated?
    PO_B:
        Backend obligation — backend witness can validate executability?
    """

    PO_E: bool
    PO_A: bool
    PO_M: bool
    PO_U: bool
    PO_B: bool


@dataclass
class ConsequenceSignature:
    """Consequence signature chi(C) computed by the MCS stage (Section 3.5).

    Attributes
    ----------
    executability:
        Overall executability score [0, 1].
    hard_goals:
        List of hard goals that must be achieved.
    optional_goals:
        List of optional / soft goals.
    sequence_closure:
        Ordered sequence of actions (plan closure).
    min_energy_margin:
        Minimum energy margin over the plan (Wh).
    min_time_margin:
        Minimum time margin over the plan (seconds).
    airspace_compliance:
        Airspace compliance score [0, 1].
    communication_feasibility:
        Communication feasibility score [0, 1].
    payload_satisfaction:
        Payload requirement satisfaction [0, 1].
    weather_satisfaction:
        Weather constraint satisfaction [0, 1].
    """

    executability: float
    hard_goals: List[str]
    optional_goals: List[str]
    sequence_closure: List[str]
    min_energy_margin: float
    min_time_margin: float
    airspace_compliance: float
    communication_feasibility: float
    payload_satisfaction: float
    weather_satisfaction: float


@dataclass
class MAC:
    """Mission Admission Contract output by the EAMSR pipeline (Section 3).

    Contains structured clauses, proof obligations, consequence signature, and
    the final admission decision.

    Attributes
    ----------
    contract_id:
        Unique identifier. Format: ``MAC-{sample_id}-{candidate_number}``.
    sample_id:
        Reference to the parent MissionSample.
    clauses:
        All clauses in the contract.
    hard_obligations:
        Clause IDs classified as hard obligations H_i.
    soft_obligations:
        Clause IDs classified as soft obligations S_i.
    pending_set:
        Clause IDs that require clarification P_i.
    po_results:
        Results of the five proof obligations.
    consequence_signature:
        Computed consequence signature chi(C).
    decision:
        Final admission decision.
    audit_trail_id:
        Reference to the audit trail document.
    """

    contract_id: str
    sample_id: str
    clauses: List[MACClause]
    hard_obligations: List[str]
    soft_obligations: List[str]
    pending_set: List[str]
    po_results: ProofObligations
    consequence_signature: ConsequenceSignature
    decision: str
    audit_trail_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialise this MAC to a JSON-compatible dict."""
        return _as_dict(self)  # type: ignore[return-value]


# =============================================================================
# Schema 3 — ExperimentResult
# =============================================================================

@dataclass
class WitnessAction:
    """A single action in the witness plan."""

    action_type: str
    start_time: float
    end_time: float
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WitnessPlan:
    """Backend witness plan pi produced when decision is ACCEPT (Section 3.5).

    Attributes
    ----------
    actions:
        Ordered list of planned actions.
    energy_profile:
        Predicted battery level over time.
    position_profile:
        Predicted position over time.
    constraints_check:
        Per-constraint satisfaction status (constraint_id -> bool).
    """

    actions: List[WitnessAction]
    energy_profile: List[Dict[str, float]]
    position_profile: List[Dict[str, float]]
    constraints_check: Dict[str, bool]


@dataclass
class ConfusionMatrix:
    """3x3 confusion matrix for admission decisions.

    Attributes
    ----------
    rows:
        Row labels (predicted): ACCEPT, CLARIFY, REJECT.
    columns:
        Column labels (ground truth): ACCEPT, CLARIFY, REJECT.
    values:
        3x3 integer count matrix.
    """

    rows: List[str]
    columns: List[str]
    values: List[List[int]]


@dataclass
class Metrics:
    """Evaluation metrics for a single experimental run (Section 4).

    Attributes
    ----------
    Acc_adm:
        Admission accuracy — fraction of correct decisions.
    UAR:
        Unsafe admission rate — unsafe missions incorrectly accepted.
    ECR:
        Evidence coverage rate — claims grounded in evidence.
    UBR:
        Unverified belief / hypothesis block rate — LLM assumptions blocked.
    PIR:
        Protected invariant retention rate — invariants preserved.
    WSR:
        Witness success rate — backend plans validated successfully.
    CNR:
        Clarification necessity rate — appropriate CLARIFY decisions.
    ATR:
        Audit trail completeness rate — full auditability achieved.
    """

    Acc_adm: float
    UAR: float
    ECR: float
    UBR: float
    PIR: float
    WSR: float
    CNR: float
    ATR: float


@dataclass
class BudgetUsed:
    """Computational budget consumed by a run.

    Attributes
    ----------
    candidates_generated:
        Number of MAC candidates generated.
    refinement_rounds:
        Number of refinement iterations.
    total_calls:
        Total LLM or backend API calls.
    """

    candidates_generated: int
    refinement_rounds: int
    total_calls: int


@dataclass
class ExperimentResult:
    """Result of running a single experimental method on a single mission sample
    (Section 4).

    Attributes
    ----------
    run_id:
        Unique identifier.
        Format: ``RUN-{method}-{sample_id}-{run_number}``.
    method:
        Experimental method / ablation condition.
    sample_id:
        Reference to the MissionSample.
    predicted_decision:
        Decision produced by the method.
    confusion_matrix:
        3x3 confusion matrix against ground truth.
    metrics:
        Eight evaluation metrics.
    witness_plan:
        Witness plan if ``predicted_decision == "ACCEPT"``, else ``None``.
    runtime_seconds:
        Wall-clock runtime in seconds.
    budget_used:
        Computational budget consumed.
    """

    run_id: str
    method: str
    sample_id: str
    predicted_decision: str
    confusion_matrix: ConfusionMatrix
    metrics: Metrics
    witness_plan: Optional[WitnessPlan]
    runtime_seconds: float
    budget_used: BudgetUsed

    def to_dict(self) -> Dict[str, Any]:
        """Serialise this result to a JSON-compatible dict."""
        return _as_dict(self)  # type: ignore[return-value]


# =============================================================================
# Schema loader — shared JSON Schema document
# =============================================================================

# In-memory cache for the loaded schema document.
_SCHEMA_DOC: Optional[Dict[str, Any]] = None


def _load_schema_doc() -> Dict[str, Any]:
    """Load the bundled JSON Schema document.

    The function first looks for ``eamsr_schemas.json`` in the same directory
    as this module, then falls back to the current working directory.

    Returns
    -------
    dict
        The complete JSON Schema document (Draft 7) containing definitions for
        MissionSample, MAC, and ExperimentResult.

    Raises
    ------
    FileNotFoundError
        If the JSON schema file cannot be located.
    json.JSONDecodeError
        If the file is not valid JSON.
    """
    global _SCHEMA_DOC  # noqa: PLW0603
    if _SCHEMA_DOC is not None:
        return _SCHEMA_DOC

    module_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(module_dir, "eamsr_schemas.json"),
        os.path.join(os.getcwd(), "eamsr_schemas.json"),
        os.path.join(module_dir, "..", "eamsr_schemas.json"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                _SCHEMA_DOC = json.load(fh)
            return _SCHEMA_DOC  # type: ignore[return-value]

    raise FileNotFoundError(
        "eamsr_schemas.json not found. Searched: " + "; ".join(candidates)
    )


# =============================================================================
# get_schema — public schema accessor
# =============================================================================

def get_schema(schema_name: str) -> Dict[str, Any]:
    """Return the JSON Schema dict for a named schema.

    Parameters
    ----------
    schema_name:
        One of ``"MissionSample"``, ``"MAC"``, or ``"ExperimentResult"``.

    Returns
    -------
    dict
        A JSON Schema (Draft 7) dictionary that can be used directly with
        ``jsonschema.validate`` or ``Draft7Validator``.

    Raises
    ------
    KeyError
        If *schema_name* is not recognised.

    Examples
    --------
    >>> schema = get_schema("MissionSample")
    >>> jsonschema.validate(my_data, schema)
    """
    doc = _load_schema_doc()
    if schema_name not in doc.get("properties", {}):
        raise KeyError(
            f"Unknown schema '{schema_name}'. "
            f"Choose from: MissionSample, MAC, ExperimentResult"
        )

    # Build a self-contained schema by inlining the definitions.
    schema = doc["properties"][schema_name].copy()
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    schema["definitions"] = doc.get("definitions", {})
    return schema


# =============================================================================
# Validation helpers
# =============================================================================

def validate_mission_sample(data: Dict[str, Any]) -> None:
    """Validate a dict against the **MissionSample** JSON Schema.

    Parameters
    ----------
    data:
        Dictionary representing a mission sample.

    Raises
    ------
    jsonschema.ValidationError
        If *data* does not conform to the MissionSample schema.
    RuntimeError
        If ``jsonschema`` is not installed.

    Examples
    --------
    >>> sample = {"sample_id": "MS-S1-T1-explicit-01", ...}
    >>> validate_mission_sample(sample)  # passes silently on success
    """
    if not _HAS_JSONSCHEMA:
        raise RuntimeError(
            "The 'jsonschema' package is required for validation. "
            "Install it with: pip install jsonschema"
        )
    schema = get_schema("MissionSample")
    _jsonschema_validate(instance=data, schema=schema)


def validate_mac(data: Dict[str, Any]) -> None:
    """Validate a dict against the **MAC** JSON Schema.

    Parameters
    ----------
    data:
        Dictionary representing a Mission Admission Contract.

    Raises
    ------
    jsonschema.ValidationError
        If *data* does not conform to the MAC schema.
    RuntimeError
        If ``jsonschema`` is not installed.

    Examples
    --------
    >>> mac = {"contract_id": "MAC-MS-S1-T1-explicit-01-1", ...}
    >>> validate_mac(mac)  # passes silently on success
    """
    if not _HAS_JSONSCHEMA:
        raise RuntimeError(
            "The 'jsonschema' package is required for validation. "
            "Install it with: pip install jsonschema"
        )
    schema = get_schema("MAC")
    _jsonschema_validate(instance=data, schema=schema)


def validate_experiment_result(data: Dict[str, Any]) -> None:
    """Validate a dict against the **ExperimentResult** JSON Schema.

    Parameters
    ----------
    data:
        Dictionary representing an experimental result.

    Raises
    ------
    jsonschema.ValidationError
        If *data* does not conform to the ExperimentResult schema.
    RuntimeError
        If ``jsonschema`` is not installed.

    Examples
    --------
    >>> result = {"run_id": "RUN-Full_EAMSR-MS-S1-T1-explicit-01-1", ...}
    >>> validate_experiment_result(result)  # passes silently on success
    """
    if not _HAS_JSONSCHEMA:
        raise RuntimeError(
            "The 'jsonschema' package is required for validation. "
            "Install it with: pip install jsonschema"
        )
    schema = get_schema("ExperimentResult")
    _jsonschema_validate(instance=data, schema=schema)


# =============================================================================
# Convenience: validate any of the three top-level schemas
# =============================================================================

def validate(data: Dict[str, Any], schema_name: str) -> None:
    """Validate *data* against the named schema.

    Parameters
    ----------
    data:
        Dictionary to validate.
    schema_name:
        One of ``"MissionSample"``, ``"MAC"``, ``"ExperimentResult"``.

    Raises
    ------
    jsonschema.ValidationError
        If validation fails.
    KeyError
        If *schema_name* is not recognised.
    RuntimeError
        If ``jsonschema`` is not installed.
    """
    if not _HAS_JSONSCHEMA:
        raise RuntimeError(
            "The 'jsonschema' package is required for validation. "
            "Install it with: pip install jsonschema"
        )
    schema = get_schema(schema_name)
    _jsonschema_validate(instance=data, schema=schema)


# =============================================================================
# Module-level sanity check (executed on import in __main__ context)
# =============================================================================

if __name__ == "__main__":
    # Quick sanity check: load schemas and validate the JSON Schema itself.
    doc = _load_schema_doc()
    if _HAS_JSONSCHEMA:
        Draft7Validator.check_schema(doc)
        print("JSON Schema document is valid Draft 7.")
    print("eamsr_schemas module loaded successfully.")
