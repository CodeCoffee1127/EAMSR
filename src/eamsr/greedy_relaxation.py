"""
greedy_relaxation.py — Greedy Relaxation Baseline for EAMSR

This module implements the Greedy Relaxation baseline for the EAMSR (Evidence-carrying
Autonomous Mission Safety & Reasoning) experimental framework. When a Mission Admission
Candidate (MAC) fails the Backend Witness (i.e., the task plan is physically infeasible),
this baseline applies a fixed-priority relaxation strategy to make the infeasible MAC
feasible again.

In the experiment framework, this baseline is referred to as "STL-style Repair" and is
used as a comparison method against the full EAMSR refinement pipeline (permission-bounded
refinement + mission consequence clarification).

References
----------
- Method Doc Section 3.4: Permission-bounded Refinement and Mission Consequence
  Clarification. The Greedy Relaxation baseline provides a simplified alternative that
  does NOT perform consequence clarification — it greedily relaxes constraints in a
  fixed priority order until feasibility is achieved or candidates are exhausted.
- Experiment Doc Section 4.1.2 (Baselines — STL-style Repair): This baseline is listed
  as "STL-style Repair" in Table 3 and Table 6. It follows a fixed-priority relaxation
  order without structured consequence negotiation.
- Experiment Doc Section 4.5 (Refinement, Clarification, and Repair Comparison):
  Compares the full EAMSR refinement pipeline against Greedy Relaxation on metrics
  including success rate, average relaxation cost, number of clarification rounds, and
  protected invariant preservation rate.

Algorithm Overview
------------------
The Greedy Relaxation algorithm operates as follows:

1. **Identify relaxable clauses** from the MAC. A clause is relaxable if its mode is
   "soft", "optional", or "pending", and its type is one of the supported constraint
   categories. Hard constraints (user_explicit with mode="hard", protected invariants,
   and evidence-supported hard constraints) are NEVER relaxed.

2. **Group relaxable clauses by type** following a FIXED priority order:
   temporal > spatial > communication > payload.

3. **For each priority group**, attempt three relaxation actions in order:
   - ``weaken``: Reduce constraint strength by 20% (e.g., widen time windows,
     reduce coverage area, downgrade communication bandwidth, lower sensor resolution).
   - ``drop``: Remove soft/optional clauses entirely (mode="dropped").
   - ``default``: Replace the clause with a matching system default.

4. **After each modification**, estimate feasibility via a mock backend check.
   If the backend passes, the candidate is marked as feasible.

5. **Stopping conditions**: Stop when any of the following occurs:
   - Backend PO passes (feasibility verified).
   - All relaxable items at all priority levels are exhausted.
   - Maximum of MAX_CANDIDATES candidates generated (Bc=3 sub-budget).
   - Protected invariants would be violated by further relaxation.

6. **Sort all candidates** by total relaxation cost (ascending) and return the top
   candidates (at most max_candidates).

Hard Constraints (NEVER Violated)
----------------------------------
- **I_prot** (protected invariants): return reserve, no-fly zones, geofence,
  altitude limits, payload max, emergency conditions.
- **User hard intent**: clauses with mode="hard" that came from user_explicit source.
- **Evidence-supported hard constraints**: clauses with semantic_support="Y" and
  mode="hard".

Author: EAMSR Baseline Implementations
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ──────────────────────────────────────────────────────────────────────────────
# Frozen Parameters
# ──────────────────────────────────────────────────────────────────────────────

RELAXATION_PRIORITY: List[str] = ["temporal", "spatial", "communication", "payload"]
"""Fixed relaxation priority order: temporal > spatial > communication > payload."""

MAX_CANDIDATES: int = 3
"""Maximum number of relaxation candidates to generate (Bc sub-budget)."""

WEAKEN_FACTOR: float = 0.20
"""Percentage by which to weaken a constraint (20%)."""

BUDGET_CANDIDATE: int = 5
"""Frozen parameter: overall candidate budget."""

BUDGET_REFINEMENT: int = 3
"""Frozen parameter: refinement sub-budget."""


# ──────────────────────────────────────────────────────────────────────────────
# Core Data Structures
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class RelaxationAction:
    """A single relaxation action applied to a clause.

    Records the modification made to a clause during the greedy relaxation process,
    including the type of action, the before/after state, the semantic drift cost,
    and a human-readable description.

    Attributes
    ----------
    clause_id : str
        Which clause is being modified (unique clause identifier).
    action_type : str
        Type of relaxation action: "weaken", "drop", or "default".
    original_value : dict
        Original clause state before relaxation.
    new_value : dict
        Modified clause state after relaxation.
    cost : float
        Relaxation cost (semantic drift) of this action.
    description : str
        Human-readable description of what was changed.
    """

    clause_id: str
    action_type: str
    original_value: dict
    new_value: dict
    cost: float
    description: str


@dataclass
class RelaxationCandidate:
    """A candidate relaxed MAC produced by the greedy relaxation algorithm.

    Represents one possible relaxed version of the original MAC, along with the
    sequence of relaxation actions that produced it and metadata about its quality.

    Attributes
    ----------
    mac_id : str
        Parent MAC ID (identifier of the original infeasible MAC).
    candidate_id : str
        Unique candidate number (e.g., "cand_0", "cand_1").
    relaxed_clauses : List[dict]
        The modified clause list for this candidate.
    relaxation_actions : List[RelaxationAction]
        Ordered list of relaxation actions applied to produce this candidate.
    total_cost : float
        Cumulative relaxation cost (sum of individual action costs).
    satisfies_backend : bool
        Whether this candidate passes the Backend PO (mock for P0).
    satisfies_protected : bool
        Whether I_prot (protected invariants) is preserved.
    estimated_feasibility : float
        0-1 estimated feasibility score from the mock estimator.
    """

    mac_id: str
    candidate_id: str
    relaxed_clauses: List[dict]
    relaxation_actions: List[RelaxationAction]
    total_cost: float
    satisfies_backend: bool
    satisfies_protected: bool
    estimated_feasibility: float


# ──────────────────────────────────────────────────────────────────────────────
# Helper: Deep copy utilities
# ──────────────────────────────────────────────────────────────────────────────


def _deep_copy_clauses(clauses: List[dict]) -> List[dict]:
    """Return a deep copy of a list of clause dictionaries."""
    return copy.deepcopy(clauses)


def _clause_to_hashable(clause: dict) -> str:
    """Convert a clause dict to a hashable string for deterministic checks."""
    return json.dumps(clause, sort_keys=True, default=str)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Main Interface Function
# ──────────────────────────────────────────────────────────────────────────────


def greedy_relaxation(
    mac: dict,
    conflict_core: dict,
    max_candidates: int = MAX_CANDIDATES,
) -> List[dict]:
    """Apply greedy relaxation to an infeasible MAC to produce relaxed candidates.

    This is the main interface function for the Greedy Relaxation baseline
    ("STL-style Repair"). It attempts to make an infeasible MAC feasible by
    greedily relaxing soft/optional constraints in a fixed priority order.

    Parameters
    ----------
    mac : dict
        The infeasible MAC dict, expected to have at least:
        - "mac_id": str — unique identifier
        - "clauses": List[dict] — list of clause dictionaries, each with:
          - "clause_id": str
          - "clause_type": str ("temporal", "spatial", "communication", "payload")
          - "mode": str ("hard", "soft", "optional", "pending")
          - "source": str ("user_explicit", "derived", "system", etc.)
          - "formal_semantic": dict — structured semantic representation
          - Optional: "semantic_support": str ("Y" or "N")
          - Optional: "protected_constraint": bool
    conflict_core : dict
        Conflict analysis result from the l1_simulator with fields:
        - "conflicting_clauses": list of clause IDs causing the conflict
        - "unsatisfied_constraint_type": str ("SafeRTH", "GeoSafe", "AuxOK")
        - "affected_consequence_dimensions": list of str
        - "diagnosis": str — human-readable diagnosis
        - "refinement_hints": list of str — suggested refinement directions
    max_candidates : int, optional
        Maximum number of candidates to generate (default: MAX_CANDIDATES).

    Returns
    -------
    List[dict]
        At most ``max_candidates`` relaxed MAC dicts, sorted by total_cost
        ascending (cheapest first). Each dict contains:
        - "mac_id": str
        - "candidate_id": str
        - "clauses": List[dict] — the relaxed clause list
        - "relaxation_actions": List[dict] — serialized RelaxationAction records
        - "total_cost": float
        - "satisfies_backend": bool
        - "satisfies_protected": bool
        - "estimated_feasibility": float
    """
    mac_id: str = mac.get("mac_id", "unknown_mac")
    original_clauses: List[dict] = mac.get("clauses", [])

    # Step 1: Identify relaxable clauses
    relaxable_clauses: List[dict] = [
        c for c in original_clauses if is_relaxable(c)
    ]

    if not relaxable_clauses:
        return []

    # Step 2: Group relaxable clauses by type following RELAXATION_PRIORITY
    clauses_by_type: Dict[str, List[dict]] = {ptype: [] for ptype in RELAXATION_PRIORITY}
    for clause in relaxable_clauses:
        ctype = clause.get("clause_type", "")
        if ctype in clauses_by_type:
            clauses_by_type[ctype].append(clause)

    # System defaults (can be overridden by caller via mac metadata)
    defaults: dict = mac.get("system_defaults", {})

    candidates: List[RelaxationCandidate] = []
    candidate_counter: int = 0

    # Collect all clauses in priority order
    ordered_clauses: List[Tuple[str, dict]] = []
    for ptype in RELAXATION_PRIORITY:
        for clause in clauses_by_type.get(ptype, []):
            ordered_clauses.append((ptype, clause))

    # Step 3: For each priority group, try weaken → drop → default
    for ptype, clause in ordered_clauses:
        if len(candidates) >= max_candidates:
            break

        clause_id = clause.get("clause_id", "unknown")

        # --- Try "weaken" ---
        if len(candidates) < max_candidates:
            weakened = apply_weaken(clause)
            if weakened is not None:
                new_clauses = _replace_clause(original_clauses, clause, weakened)
                relaxed_mac = _build_mac(mac, new_clauses)
                if check_protected_invariants_preserved(mac, relaxed_mac):
                    action = RelaxationAction(
                        clause_id=clause_id,
                        action_type="weaken",
                        original_value=clause.get("formal_semantic", {}),
                        new_value=weakened.get("formal_semantic", {}),
                        cost=compute_relaxation_cost(clause, weakened),
                        description=f"Weakened {ptype} clause '{clause_id}': "
                                    f"reduced constraint strength by {WEAKEN_FACTOR*100:.0f}%",
                    )
                    total_cost = action.cost
                    satisfies_backend = mock_backend_check(relaxed_mac)
                    satisfies_protected = True  # verified above
                    feasibility = estimate_feasibility(relaxed_mac)

                    candidate = RelaxationCandidate(
                        mac_id=mac_id,
                        candidate_id=f"cand_{candidate_counter}",
                        relaxed_clauses=new_clauses,
                        relaxation_actions=[action],
                        total_cost=total_cost,
                        satisfies_backend=satisfies_backend,
                        satisfies_protected=satisfies_protected,
                        estimated_feasibility=feasibility,
                    )
                    candidates.append(candidate)
                    candidate_counter += 1

                    # Stopping condition: Backend PO passes
                    if satisfies_backend:
                        break

        # --- Try "drop" (only for soft/optional) ---
        if len(candidates) < max_candidates:
            mode = clause.get("mode", "")
            if mode in ("soft", "optional"):
                dropped = apply_drop(clause)
                if dropped is not None:
                    new_clauses = _replace_clause(original_clauses, clause, dropped)
                    relaxed_mac = _build_mac(mac, new_clauses)
                    if check_protected_invariants_preserved(mac, relaxed_mac):
                        action = RelaxationAction(
                            clause_id=clause_id,
                            action_type="drop",
                            original_value=clause.get("formal_semantic", {}),
                            new_value=dropped.get("formal_semantic", {}),
                            cost=compute_relaxation_cost(clause, dropped),
                            description=f"Dropped {ptype} clause '{clause_id}': "
                                        f"removed optional constraint",
                        )
                        total_cost = action.cost
                        satisfies_backend = mock_backend_check(relaxed_mac)
                        satisfies_protected = True
                        feasibility = estimate_feasibility(relaxed_mac)

                        candidate = RelaxationCandidate(
                            mac_id=mac_id,
                            candidate_id=f"cand_{candidate_counter}",
                            relaxed_clauses=new_clauses,
                            relaxation_actions=[action],
                            total_cost=total_cost,
                            satisfies_backend=satisfies_backend,
                            satisfies_protected=satisfies_protected,
                            estimated_feasibility=feasibility,
                        )
                        candidates.append(candidate)
                        candidate_counter += 1

                        if satisfies_backend:
                            break

        # --- Try "default" ---
        if len(candidates) < max_candidates:
            defaulted = apply_default(clause, defaults)
            if defaulted is not None:
                new_clauses = _replace_clause(original_clauses, clause, defaulted)
                relaxed_mac = _build_mac(mac, new_clauses)
                if check_protected_invariants_preserved(mac, relaxed_mac):
                    action = RelaxationAction(
                        clause_id=clause_id,
                        action_type="default",
                        original_value=clause.get("formal_semantic", {}),
                        new_value=defaulted.get("formal_semantic", {}),
                        cost=compute_relaxation_cost(clause, defaulted),
                        description=f"Applied default to {ptype} clause '{clause_id}': "
                                    f"replaced with system default",
                    )
                    total_cost = action.cost
                    satisfies_backend = mock_backend_check(relaxed_mac)
                    satisfies_protected = True
                    feasibility = estimate_feasibility(relaxed_mac)

                    candidate = RelaxationCandidate(
                        mac_id=mac_id,
                        candidate_id=f"cand_{candidate_counter}",
                        relaxed_clauses=new_clauses,
                        relaxation_actions=[action],
                        total_cost=total_cost,
                        satisfies_backend=satisfies_backend,
                        satisfies_protected=satisfies_protected,
                        estimated_feasibility=feasibility,
                    )
                    candidates.append(candidate)
                    candidate_counter += 1

                    if satisfies_backend:
                        break

    # Step 4: Sort candidates by total_cost ascending
    candidates.sort(key=lambda c: c.total_cost)

    # Step 5: Return top max_candidates (or fewer if stopped early)
    top_candidates = candidates[:max_candidates]

    # Serialize to dicts for return
    return [_serialize_candidate(c) for c in top_candidates]


# ──────────────────────────────────────────────────────────────────────────────
# 2. Clause Relaxability Check
# ──────────────────────────────────────────────────────────────────────────────


def is_relaxable(clause: dict) -> bool:
    """Check if a clause can be relaxed.

    A clause is relaxable if and only if ALL of the following hold:
    1. Its ``mode`` is one of "soft", "optional", or "pending".
    2. Its ``clause_type`` is one of "temporal", "spatial", "communication",
       or "payload".
    3. It is NOT a protected invariant (no ``protected_constraint=True`` marker).
    4. It is NOT a user hard intent (not from ``source="user_explicit"`` with
       ``mode="hard"``).
    5. It is NOT an evidence-supported hard constraint (not both
       ``semantic_support="Y"`` and ``mode="hard"``).

    Parameters
    ----------
    clause : dict
        Clause dictionary with fields such as ``clause_id``, ``clause_type``,
        ``mode``, ``source``, ``formal_semantic``, and optional markers.

    Returns
    -------
    bool
        ``True`` if the clause can be relaxed; ``False`` otherwise.
    """
    mode = clause.get("mode", "")
    ctype = clause.get("clause_type", "")
    source = clause.get("source", "")
    semantic_support = clause.get("semantic_support", "")
    protected = clause.get("protected_constraint", False)

    # Check mode is relaxable
    if mode not in ("soft", "optional", "pending"):
        return False

    # Check type is supported
    if ctype not in RELAXATION_PRIORITY:
        return False

    # Check not a protected invariant
    if protected is True:
        return False

    # Check not user hard intent
    if source == "user_explicit" and mode == "hard":
        return False

    # Check not evidence-supported hard constraint
    if semantic_support == "Y" and mode == "hard":
        return False

    return True


# ──────────────────────────────────────────────────────────────────────────────
# 3. Apply Weaken Transformation
# ──────────────────────────────────────────────────────────────────────────────


def apply_weaken(clause: dict) -> Optional[dict]:
    """Apply a weaken transformation to a clause.

    Reduces the constraint strength by ``WEAKEN_FACTOR`` (20%) depending on the
    clause type:

    - **temporal**: increase deadline by 20%, widen time window.
    - **spatial**: reduce coverage radius by 20%, simplify polygon complexity.
    - **communication**: downgrade bandwidth requirement by one tier.
    - **payload**: reduce resolution/quality requirement by 20%.

    Parameters
    ----------
    clause : dict
        Original clause dictionary with ``clause_type`` and ``formal_semantic``.

    Returns
    -------
    dict or None
        Weakened clause dict, or ``None`` if the clause type is not supported
        or the clause cannot be weakened.
    """
    ctype = clause.get("clause_type", "")
    weakened = copy.deepcopy(clause)
    fs = weakened.get("formal_semantic", {})

    if ctype == "temporal":
        # Increase deadline by 20%, widen window
        deadline = fs.get("deadline_seconds")
        window_start = fs.get("window_start")
        window_end = fs.get("window_end")

        if deadline is not None:
            new_deadline = deadline * (1.0 + WEAKEN_FACTOR)
            fs["deadline_seconds"] = new_deadline
        if window_start is not None and window_end is not None:
            window_width = window_end - window_start
            new_width = window_width * (1.0 + WEAKEN_FACTOR)
            midpoint = (window_start + window_end) / 2.0
            fs["window_start"] = midpoint - new_width / 2.0
            fs["window_end"] = midpoint + new_width / 2.0
        elif window_end is not None:
            fs["window_end"] = window_end * (1.0 + WEAKEN_FACTOR)

        weakened["formal_semantic"] = fs
        weakened["_relaxed"] = True
        weakened["_relaxation_type"] = "weaken"
        return weakened

    elif ctype == "spatial":
        # Reduce coverage radius by 20%, simplify polygon
        radius = fs.get("coverage_radius_m")
        if radius is not None:
            fs["coverage_radius_m"] = radius * (1.0 - WEAKEN_FACTOR)

        polygon_vertices = fs.get("polygon_vertices")
        if polygon_vertices is not None and len(polygon_vertices) > 3:
            # Simplify: keep every other vertex (reduce by ~50%)
            fs["polygon_vertices"] = polygon_vertices[::2]

        weakened["formal_semantic"] = fs
        weakened["_relaxed"] = True
        weakened["_relaxation_type"] = "weaken"
        return weakened

    elif ctype == "communication":
        # Downgrade bandwidth requirement by one tier
        bandwidth = fs.get("bandwidth_mbps")
        if bandwidth is not None:
            tiers = [100, 50, 20, 10, 5, 1, 0.5]
            current_tier = None
            for i, t in enumerate(tiers):
                if bandwidth >= t:
                    current_tier = i
                    break
            if current_tier is not None and current_tier + 1 < len(tiers):
                fs["bandwidth_mbps"] = tiers[current_tier + 1]
            else:
                fs["bandwidth_mbps"] = bandwidth * (1.0 - WEAKEN_FACTOR)

        # Also downgrade real-time requirement if present
        if fs.get("requires_real_time", False):
            fs["requires_real_time"] = False
            fs["communication_mode"] = "delayed"

        weakened["formal_semantic"] = fs
        weakened["_relaxed"] = True
        weakened["_relaxation_type"] = "weaken"
        return weakened

    elif ctype == "payload":
        # Reduce resolution/quality requirement by 20%
        resolution = fs.get("resolution_m")
        if resolution is not None:
            fs["resolution_m"] = resolution * (1.0 + WEAKEN_FACTOR)

        quality = fs.get("quality_level")
        if quality is not None:
            quality_levels = ["high", "medium", "low", "minimal"]
            if quality in quality_levels:
                idx = quality_levels.index(quality)
                if idx + 1 < len(quality_levels):
                    fs["quality_level"] = quality_levels[idx + 1]

        weight = fs.get("sensor_weight_kg")
        if weight is not None:
            fs["sensor_weight_kg"] = weight * (1.0 - WEAKEN_FACTOR)

        weakened["formal_semantic"] = fs
        weakened["_relaxed"] = True
        weakened["_relaxation_type"] = "weaken"
        return weakened

    return None


# ──────────────────────────────────────────────────────────────────────────────
# 4. Apply Drop Transformation
# ──────────────────────────────────────────────────────────────────────────────


def apply_drop(clause: dict) -> Optional[dict]:
    """Apply a drop transformation to a clause.

    Marks the clause as dropped by setting its mode to ``"dropped"`` and
    clearing its ``formal_semantic``. Only clauses with ``mode`` in
    ``["soft", "optional"]`` can be dropped.

    Parameters
    ----------
    clause : dict
        Original clause dictionary with a ``mode`` field.

    Returns
    -------
    dict or None
        Modified clause dict with ``mode="dropped"`` and empty
        ``formal_semantic``, or ``None`` if the clause is hard and
        cannot be dropped.
    """
    mode = clause.get("mode", "")
    if mode not in ("soft", "optional"):
        return None

    dropped = copy.deepcopy(clause)
    dropped["mode"] = "dropped"
    dropped["formal_semantic"] = {}
    dropped["_relaxed"] = True
    dropped["_relaxation_type"] = "drop"
    return dropped


# ──────────────────────────────────────────────────────────────────────────────
# 5. Apply Default Transformation
# ──────────────────────────────────────────────────────────────────────────────


def apply_default(clause: dict, defaults: dict) -> Optional[dict]:
    """Apply a default transformation to a clause.

    Replaces the clause's ``formal_semantic`` with a matching system default
    value. The match is determined by the clause's ``clause_type``.

    Parameters
    ----------
    clause : dict
        Original clause dictionary with ``clause_type`` and ``formal_semantic``.
    defaults : dict
        System defaults dictionary keyed by clause type. Expected structure:
        ``{"temporal": {...}, "spatial": {...}, "communication": {...},
        "payload": {...}}``.

    Returns
    -------
    dict or None
        Modified clause dict with ``formal_semantic`` replaced by the matching
        default, or ``None`` if no matching default exists for the clause type.
    """
    ctype = clause.get("clause_type", "")
    if ctype not in defaults:
        return None

    default_value = defaults[ctype]
    defaulted = copy.deepcopy(clause)
    defaulted["formal_semantic"] = copy.deepcopy(default_value)
    defaulted["_relaxed"] = True
    defaulted["_relaxation_type"] = "default"
    return defaulted


# ──────────────────────────────────────────────────────────────────────────────
# 6. Compute Relaxation Cost
# ──────────────────────────────────────────────────────────────────────────────


def compute_relaxation_cost(original: dict, modified: dict) -> float:
    """Compute the semantic drift cost of a relaxation action.

    The cost depends on the action type:

    - **weaken**: 0.5 * relative_change_in_constraint_strength
    - **drop**: 1.0 (fixed higher cost for complete removal)
    - **default**: 0.3 (fixed lowest cost for standard replacement)

    An additional priority penalty is applied for relaxing higher-priority
    constraints first, encouraging lower-cost relaxations on lower-priority
    clauses.

    Parameters
    ----------
    original : dict
        Original clause dictionary.
    modified : dict
        Modified (relaxed) clause dictionary.

    Returns
    -------
    float
        Relaxation cost (semantic drift). Higher values indicate greater
        deviation from the original intent.
    """
    action_type = modified.get("_relaxation_type", "")
    ctype = original.get("clause_type", "")
    orig_fs = original.get("formal_semantic", {})
    mod_fs = modified.get("formal_semantic", {})

    # Base cost by action type
    if action_type == "weaken":
        base_cost = 0.5 * _compute_relative_change(orig_fs, mod_fs)
    elif action_type == "drop":
        base_cost = 1.0
    elif action_type == "default":
        base_cost = 0.3
    else:
        base_cost = 0.5

    # Priority penalty: higher priority types get additional cost
    # This reflects that relaxing temporal constraints is more semantically
    # impactful than relaxing payload constraints.
    priority_index = RELAXATION_PRIORITY.index(ctype) if ctype in RELAXATION_PRIORITY else len(RELAXATION_PRIORITY)
    priority_penalty = priority_index * 0.1

    return round(base_cost + priority_penalty, 4)


def _compute_relative_change(orig: dict, mod: dict) -> float:
    """Compute a normalized relative change between two formal_semantic dicts.

    Extracts all numeric fields from both dicts and computes the average
    absolute relative change. Returns 0.0 if no numeric fields are found.

    Parameters
    ----------
    orig : dict
        Original formal_semantic dict.
    mod : dict
        Modified formal_semantic dict.

    Returns
    -------
    float
        Average absolute relative change (capped at 1.0).
    """
    numeric_orig = _extract_numeric_values(orig)
    numeric_mod = _extract_numeric_values(mod)

    if not numeric_orig:
        return 0.0

    total_change = 0.0
    count = 0
    for key, orig_val in numeric_orig.items():
        mod_val = numeric_mod.get(key, orig_val)
        if orig_val != 0:
            rel_change = abs((mod_val - orig_val) / orig_val)
        else:
            rel_change = 0.0 if mod_val == 0 else 1.0
        total_change += min(rel_change, 1.0)
        count += 1

    return total_change / max(count, 1)


def _extract_numeric_values(d: dict, prefix: str = "") -> Dict[str, float]:
    """Recursively extract all numeric values from a nested dict.

    Parameters
    ----------
    d : dict
        Dictionary to extract numeric values from.
    prefix : str, optional
        Key prefix for nested fields.

    Returns
    -------
    Dict[str, float]
        Flattened mapping of dotted key paths to numeric values.
    """
    result: Dict[str, float] = {}
    for key, value in d.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            result[full_key] = float(value)
        elif isinstance(value, dict):
            result.update(_extract_numeric_values(value, full_key))
        elif isinstance(value, list) and value and isinstance(value[0], (int, float)):
            # Handle simple numeric lists (e.g., polygon vertices as flat coords)
            for i, v in enumerate(value):
                result[f"{full_key}[{i}]"] = float(v)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# 7. Check Protected Invariants Preservation
# ──────────────────────────────────────────────────────────────────────────────


def check_protected_invariants_preserved(original_mac: dict, relaxed_mac: dict) -> bool:
    """Verify that no protected invariant was modified during relaxation.

    Compares the hard_obligations and clauses with protected_constraint markers
    between the original and relaxed MACs. All protected constraints must remain
    identical (no modification allowed).

    Parameters
    ----------
    original_mac : dict
        Original MAC dict before relaxation.
    relaxed_mac : dict
        Relaxed MAC dict after applying relaxation actions.

    Returns
    -------
    bool
        ``True`` if all protected constraints are preserved unchanged;
        ``False`` if any protected invariant was modified.
    """
    orig_clauses = original_mac.get("clauses", [])
    relaxed_clauses = relaxed_mac.get("clauses", [])

    # Build lookup of protected clauses in original
    orig_protected: Dict[str, dict] = {}
    for clause in orig_clauses:
        if clause.get("protected_constraint", False) or clause.get("mode", "") == "hard":
            cid = clause.get("clause_id", "")
            if cid:
                orig_protected[cid] = clause

    # Check that each protected clause in original exists identically in relaxed
    relaxed_clauses_by_id: Dict[str, dict] = {}
    for clause in relaxed_clauses:
        cid = clause.get("clause_id", "")
        if cid:
            relaxed_clauses_by_id[cid] = clause

    for cid, orig_clause in orig_protected.items():
        if cid not in relaxed_clauses_by_id:
            # Protected clause was removed — violation
            return False
        relaxed_clause = relaxed_clauses_by_id[cid]
        # Compare formal_semantic (the key content)
        if _clause_to_hashable(orig_clause) != _clause_to_hashable(relaxed_clause):
            # Protected clause was modified — violation
            return False

    # Also check hard obligations if present
    orig_obligations = original_mac.get("hard_obligations", [])
    relaxed_obligations = relaxed_mac.get("hard_obligations", [])
    if set(json.dumps(o, sort_keys=True, default=str) for o in orig_obligations) != \
       set(json.dumps(o, sort_keys=True, default=str) for o in relaxed_obligations):
        return False

    return True


# ──────────────────────────────────────────────────────────────────────────────
# 8. Estimate Feasibility (P0 Stub)
# ──────────────────────────────────────────────────────────────────────────────


def estimate_feasibility(relaxed_mac: dict) -> float:
    """Estimate the feasibility of a relaxed MAC.

    This is a P0 stub implementation. In P1, this function will call
    ``l1_simulator.verify_witness()`` for actual backend verification.

    The current heuristic assigns +0.15 feasibility boost for each relaxed
    clause of each supported type, capped at 1.0. This reflects the intuition
    that relaxing constraints generally increases feasibility.

    Parameters
    ----------
    relaxed_mac : dict
        The relaxed MAC dict with a ``clauses`` list.

    Returns
    -------
    float
        Estimated feasibility score in [0.0, 1.0].
    """
    clauses = relaxed_mac.get("clauses", [])
    score = 0.0

    for clause in clauses:
        if clause.get("_relaxed", False):
            ctype = clause.get("clause_type", "")
            if ctype in RELAXATION_PRIORITY:
                score += 0.15

    return min(score, 1.0)


# ──────────────────────────────────────────────────────────────────────────────
# Mock Backend Check (P0 Stub)
# ──────────────────────────────────────────────────────────────────────────────


def mock_backend_check(mac: dict) -> bool:
    """P0 stub: deterministically check if a relaxed MAC passes backend.

    Uses a seeded hash of the MAC content to produce a deterministic
    feasibility result. The hash modulo 3 determines feasibility:
    ``hash % 3 == 0`` means the MAC is deemed feasible.

    In P1, this will be replaced by ``l1_simulator.verify_witness()``.

    Parameters
    ----------
    mac : dict
        The MAC dict to check for backend feasibility.

    Returns
    -------
    bool
        ``True`` if the MAC deterministically passes the mock backend check;
        ``False`` otherwise.
    """
    content = json.dumps(mac, sort_keys=True, default=str)
    hash_value = int(hashlib.sha256(content.encode("utf-8")).hexdigest(), 16)
    return (hash_value % 3) == 0


# ──────────────────────────────────────────────────────────────────────────────
# Internal Helper Functions
# ──────────────────────────────────────────────────────────────────────────────


def _replace_clause(clauses: List[dict], old_clause: dict, new_clause: dict) -> List[dict]:
    """Return a new clause list with ``old_clause`` replaced by ``new_clause``.

    Parameters
    ----------
    clauses : List[dict]
        Original list of clause dicts.
    old_clause : dict
        Clause to replace (matched by ``clause_id``).
    new_clause : dict
        Replacement clause dict.

    Returns
    -------
    List[dict]
        Deep-copied clause list with the replacement applied.
    """
    new_clauses = _deep_copy_clauses(clauses)
    old_id = old_clause.get("clause_id", "")
    for i, c in enumerate(new_clauses):
        if c.get("clause_id", "") == old_id:
            new_clauses[i] = copy.deepcopy(new_clause)
            break
    return new_clauses


def _build_mac(original_mac: dict, new_clauses: List[dict]) -> dict:
    """Build a MAC dict with the given clause list, preserving other fields.

    Parameters
    ----------
    original_mac : dict
        Original MAC dict (deep-copied; only ``clauses`` is replaced).
    new_clauses : List[dict]
        New clause list to use.

    Returns
    -------
    dict
        New MAC dict with updated clauses.
    """
    mac = copy.deepcopy(original_mac)
    mac["clauses"] = new_clauses
    return mac


def _serialize_candidate(candidate: RelaxationCandidate) -> dict:
    """Serialize a RelaxationCandidate to a plain dict for return.

    Parameters
    ----------
    candidate : RelaxationCandidate
        The candidate to serialize.

    Returns
    -------
    dict
        Serialized candidate with all fields as plain Python objects.
    """
    return {
        "mac_id": candidate.mac_id,
        "candidate_id": candidate.candidate_id,
        "clauses": candidate.relaxed_clauses,
        "relaxation_actions": [
            {
                "clause_id": action.clause_id,
                "action_type": action.action_type,
                "original_value": action.original_value,
                "new_value": action.new_value,
                "cost": action.cost,
                "description": action.description,
            }
            for action in candidate.relaxation_actions
        ],
        "total_cost": candidate.total_cost,
        "satisfies_backend": candidate.satisfies_backend,
        "satisfies_protected": candidate.satisfies_protected,
        "estimated_feasibility": candidate.estimated_feasibility,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Test Harness
# ──────────────────────────────────────────────────────────────────────────────


def _make_test_mac(mac_id: str, clauses: List[dict]) -> dict:
    """Create a test MAC dict with the given clauses."""
    return {
        "mac_id": mac_id,
        "mission_description": f"Test mission {mac_id}",
        "clauses": clauses,
        "hard_obligations": [
            {"type": "return_reserve", "value": 0.25},
            {"type": "geofence", "max_altitude_m": 120},
        ],
        "system_defaults": {
            "temporal": {"deadline_seconds": 1800, "window_start": 0, "window_end": 1800},
            "spatial": {"coverage_radius_m": 500, "polygon_vertices": [[0, 0], [1, 0], [1, 1], [0, 1]]},
            "communication": {"bandwidth_mbps": 10, "requires_real_time": False, "communication_mode": "delayed"},
            "payload": {"resolution_m": 0.5, "quality_level": "medium", "sensor_weight_kg": 0.3},
        },
    }


def _run_tests():
    """Run all test cases for the Greedy Relaxation baseline."""

    print("=" * 70)
    print("Greedy Relaxation Baseline — STL-style Repair (P0)")
    print("=" * 70)

    # ── Test 1: MAC with temporal conflict ────────────────────────────────
    print("\n--- Test 1: MAC with temporal conflict ---")
    temporal_mac = _make_test_mac("mac_temporal_01", [
        {
            "clause_id": "c_temp_01",
            "clause_type": "temporal",
            "mode": "soft",
            "source": "derived",
            "natural_language": "Complete survey within 10 minutes",
            "formal_semantic": {
                "deadline_seconds": 600,
                "window_start": 0,
                "window_end": 600,
            },
        },
        {
            "clause_id": "c_spatial_01",
            "clause_type": "spatial",
            "mode": "hard",
            "source": "user_explicit",
            "natural_language": "Survey the northern sector",
            "formal_semantic": {"coverage_radius_m": 1000, "polygon_vertices": [[0, 0], [2, 0], [2, 2], [0, 2]]},
        },
        {
            "clause_id": "c_prot_01",
            "clause_type": "spatial",
            "mode": "hard",
            "source": "system",
            "protected_constraint": True,
            "natural_language": "No-fly zone boundary",
            "formal_semantic": {"no_fly_zone_id": "nfz_001", "boundary": [[0, 0], [1, 0], [1, 1], [0, 1]]},
        },
    ])

    conflict_temporal = {
        "conflicting_clauses": ["c_temp_01"],
        "unsatisfied_constraint_type": "SafeRTH",
        "affected_consequence_dimensions": ["time", "safety"],
        "diagnosis": "Temporal deadline too tight for return-to-home reserve",
        "refinement_hints": ["Widen time window", "Reduce survey area"],
    }

    candidates_t1 = greedy_relaxation(temporal_mac, conflict_temporal)
    print(f"  Candidates generated: {len(candidates_t1)}")
    for c in candidates_t1:
        print(f"    {c['candidate_id']}: cost={c['total_cost']:.4f}, "
              f"backend={c['satisfies_backend']}, feasibility={c['estimated_feasibility']:.2f}")
        for action in c["relaxation_actions"]:
            print(f"      -> {action['action_type']}: {action['description']} (cost={action['cost']:.4f})")

    # ── Test 2: MAC with spatial conflict ─────────────────────────────────
    print("\n--- Test 2: MAC with spatial conflict ---")
    spatial_mac = _make_test_mac("mac_spatial_01", [
        {
            "clause_id": "c_spatial_02",
            "clause_type": "spatial",
            "mode": "soft",
            "source": "derived",
            "natural_language": "Full area coverage required",
            "formal_semantic": {"coverage_radius_m": 2000, "polygon_vertices": [[0, 0], [4, 0], [4, 4], [3, 2], [2, 5], [0, 4]]},
        },
        {
            "clause_id": "c_temp_02",
            "clause_type": "temporal",
            "mode": "hard",
            "source": "user_explicit",
            "natural_language": "Must complete by 14:00",
            "formal_semantic": {"deadline_seconds": 3600, "window_start": 0, "window_end": 3600},
        },
        {
            "clause_id": "c_comm_01",
            "clause_type": "communication",
            "mode": "optional",
            "source": "derived",
            "natural_language": "Real-time video stream preferred",
            "formal_semantic": {"bandwidth_mbps": 50, "requires_real_time": True, "communication_mode": "real_time"},
        },
        {
            "clause_id": "c_prot_02",
            "clause_type": "spatial",
            "mode": "hard",
            "source": "system",
            "protected_constraint": True,
            "natural_language": "Altitude ceiling",
            "formal_semantic": {"max_altitude_m": 120},
        },
    ])

    conflict_spatial = {
        "conflicting_clauses": ["c_spatial_02"],
        "unsatisfied_constraint_type": "GeoSafe",
        "affected_consequence_dimensions": ["coverage", "safety"],
        "diagnosis": "Survey area exceeds geofence boundary",
        "refinement_hints": ["Reduce coverage area", "Split into sub-missions"],
    }

    candidates_t2 = greedy_relaxation(spatial_mac, conflict_spatial)
    print(f"  Candidates generated: {len(candidates_t2)}")
    for c in candidates_t2:
        print(f"    {c['candidate_id']}: cost={c['total_cost']:.4f}, "
              f"backend={c['satisfies_backend']}, feasibility={c['estimated_feasibility']:.2f}")
        for action in c["relaxation_actions"]:
            print(f"      -> {action['action_type']}: {action['description']} (cost={action['cost']:.4f})")

    # ── Test 3: MAC with no relaxable clauses ─────────────────────────────
    print("\n--- Test 3: MAC with no relaxable clauses ---")
    no_relax_mac = _make_test_mac("mac_norelax_01", [
        {
            "clause_id": "c_hard_01",
            "clause_type": "temporal",
            "mode": "hard",
            "source": "user_explicit",
            "natural_language": "Must depart at 09:00",
            "formal_semantic": {"deadline_seconds": 32400, "window_start": 32400, "window_end": 32400},
        },
        {
            "clause_id": "c_hard_02",
            "clause_type": "spatial",
            "mode": "hard",
            "source": "user_explicit",
            "natural_language": "Survey Zone A",
            "formal_semantic": {"coverage_radius_m": 500, "polygon_vertices": [[0, 0], [1, 0], [1, 1], [0, 1]]},
        },
        {
            "clause_id": "c_prot_03",
            "clause_type": "spatial",
            "mode": "hard",
            "source": "system",
            "protected_constraint": True,
            "natural_language": "Emergency landing zone",
            "formal_semantic": {"emergency_zone_id": "ez_001", "location": [0.5, 0.5]},
        },
    ])

    conflict_no_relax = {
        "conflicting_clauses": ["c_hard_01", "c_hard_02"],
        "unsatisfied_constraint_type": "SafeRTH",
        "affected_consequence_dimensions": ["time", "safety"],
        "diagnosis": "Mission impossible — all constraints are hard",
        "refinement_hints": ["No relaxation possible"],
    }

    candidates_t3 = greedy_relaxation(no_relax_mac, conflict_no_relax)
    print(f"  Candidates generated: {len(candidates_t3)}")
    if not candidates_t3:
        print("  (empty list as expected — no relaxable clauses)")

    # ── Test 4: Verify protected invariants never modified ────────────────
    print("\n--- Test 4: Verify protected invariants never modified ---")
    protected_mac = _make_test_mac("mac_protected_01", [
        {
            "clause_id": "c_temp_03",
            "clause_type": "temporal",
            "mode": "soft",
            "source": "derived",
            "natural_language": "Survey within 15 minutes",
            "formal_semantic": {"deadline_seconds": 900, "window_start": 0, "window_end": 900},
        },
        {
            "clause_id": "c_geofence",
            "clause_type": "spatial",
            "mode": "hard",
            "source": "system",
            "protected_constraint": True,
            "natural_language": "Geofence boundary at 120m altitude",
            "formal_semantic": {"max_altitude_m": 120, "geofence_type": "cylindrical"},
        },
        {
            "clause_id": "c_reserve",
            "clause_type": "temporal",
            "mode": "hard",
            "source": "system",
            "protected_constraint": True,
            "natural_language": "Return reserve: 25% battery",
            "formal_semantic": {"return_reserve_pct": 0.25},
        },
    ])

    conflict_protected = {
        "conflicting_clauses": ["c_temp_03"],
        "unsatisfied_constraint_type": "SafeRTH",
        "affected_consequence_dimensions": ["time"],
        "diagnosis": "Time window too tight given return reserve",
        "refinement_hints": ["Widen time window"],
    }

    candidates_t4 = greedy_relaxation(protected_mac, conflict_protected)
    print(f"  Candidates generated: {len(candidates_t4)}")
    all_protected_ok = True
    for c in candidates_t4:
        print(f"    {c['candidate_id']}: satisfies_protected={c['satisfies_protected']}")
        if not c["satisfies_protected"]:
            all_protected_ok = False
        # Deep check: verify protected clauses are unchanged
        for clause in c["clauses"]:
            if clause.get("protected_constraint", False):
                orig_clause = next(
                    (oc for oc in protected_mac["clauses"] if oc["clause_id"] == clause["clause_id"]),
                    None,
                )
                if orig_clause is not None:
                    orig_hash = _clause_to_hashable(orig_clause)
                    new_hash = _clause_to_hashable(clause)
                    if orig_hash != new_hash:
                        print(f"      VIOLATION: protected clause '{clause['clause_id']}' was modified!")
                        all_protected_ok = False

    print(f"\n  All protected invariants preserved: {all_protected_ok}")

    # ── Test 5: Multiple relaxable clause types ───────────────────────────
    print("\n--- Test 5: MAC with multiple relaxable clause types ---")
    multi_mac = _make_test_mac("mac_multi_01", [
        {
            "clause_id": "c_temp_04",
            "clause_type": "temporal",
            "mode": "soft",
            "source": "derived",
            "natural_language": "Complete within 5 minutes",
            "formal_semantic": {"deadline_seconds": 300, "window_start": 0, "window_end": 300},
        },
        {
            "clause_id": "c_spatial_04",
            "clause_type": "spatial",
            "mode": "optional",
            "source": "derived",
            "natural_language": "Cover full perimeter",
            "formal_semantic": {"coverage_radius_m": 1500, "polygon_vertices": [[0, 0], [3, 0], [3, 3], [0, 3], [0, 0]]},
        },
        {
            "clause_id": "c_comm_04",
            "clause_type": "communication",
            "mode": "soft",
            "source": "derived",
            "natural_language": "High-bandwidth telemetry",
            "formal_semantic": {"bandwidth_mbps": 100, "requires_real_time": True, "communication_mode": "real_time"},
        },
        {
            "clause_id": "c_payload_04",
            "clause_type": "payload",
            "mode": "optional",
            "source": "derived",
            "natural_language": "LIDAR scan at 0.1m resolution",
            "formal_semantic": {"resolution_m": 0.1, "quality_level": "high", "sensor_weight_kg": 1.2},
        },
        {
            "clause_id": "c_prot_04",
            "clause_type": "spatial",
            "mode": "hard",
            "source": "system",
            "protected_constraint": True,
            "natural_language": "No-fly zone alpha",
            "formal_semantic": {"no_fly_zone_id": "nfz_alpha", "boundary": [[1, 1], [2, 1], [2, 2], [1, 2]]},
        },
    ])

    conflict_multi = {
        "conflicting_clauses": ["c_temp_04", "c_spatial_04"],
        "unsatisfied_constraint_type": "AuxOK",
        "affected_consequence_dimensions": ["time", "coverage", "bandwidth"],
        "diagnosis": "Multiple soft constraints exceed platform limits",
        "refinement_hints": ["Relax temporal", "Reduce coverage", "Lower bandwidth"],
    }

    candidates_t5 = greedy_relaxation(multi_mac, conflict_multi)
    print(f"  Candidates generated: {len(candidates_t5)}")
    for c in candidates_t5:
        print(f"    {c['candidate_id']}: cost={c['total_cost']:.4f}, "
              f"backend={c['satisfies_backend']}, feasibility={c['estimated_feasibility']:.2f}")
        for action in c["relaxation_actions"]:
            print(f"      -> {action['action_type']}: {action['description']} (cost={action['cost']:.4f})")

    # ── Summary ────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"  Test 1 (temporal conflict):   {len(candidates_t1)} candidate(s)")
    print(f"  Test 2 (spatial conflict):    {len(candidates_t2)} candidate(s)")
    print(f"  Test 3 (no relaxable):        {len(candidates_t3)} candidate(s) (expected: 0)")
    print(f"  Test 4 (protected invariants): {len(candidates_t4)} candidate(s), all_preserved={all_protected_ok}")
    print(f"  Test 5 (multi-type):          {len(candidates_t5)} candidate(s)")
    print(f"\n  Total candidates across all tests: "
          f"{len(candidates_t1) + len(candidates_t2) + len(candidates_t3) + len(candidates_t4) + len(candidates_t5)}")

    if all_protected_ok and len(candidates_t3) == 0:
        print("\n  >>> ALL TESTS PASSED <<<")
    else:
        print("\n  >>> SOME TESTS FAILED <<<")

    return {
        "test1_temporal": candidates_t1,
        "test2_spatial": candidates_t2,
        "test3_no_relaxable": candidates_t3,
        "test4_protected": candidates_t4,
        "test5_multi": candidates_t5,
        "all_protected_preserved": all_protected_ok,
    }


if __name__ == "__main__":
    _run_tests()
