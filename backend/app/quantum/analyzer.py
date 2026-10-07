from dataclasses import dataclass


@dataclass
class QuantumAssessment:
    algorithm: str
    quantum_readiness_score: float
    is_vulnerable: bool
    underlying_problem: str
    quantum_threat: str
    recommendation: str
    disclaimer: str


# Scoring methodology:
# - 0-100 scale, higher = more quantum-ready
# - Based on: quantum attack applicability (40pts), standardization (20pts),
#   implementation readiness (20pts), migration compatibility (20pts)

_ALGORITHM_ASSESSMENTS = {
    "ECDSA": {
        "score": 32,
        "vulnerable": True,
        "problem": "Elliptic Curve Discrete Logarithm Problem (ECDLP)",
        "threat": (
            "Shor's algorithm can solve ECDLP in polynomial time on a sufficiently "
            "large quantum computer. Current quantum hardware is NOT capable of this. "
            "This represents a future threat model."
        ),
        "recommendation": (
            "Consider migrating to a post-quantum cryptographic algorithm. "
            "A hybrid approach (ECDSA + ML-DSA) provides transitional security."
        ),
        "breakdown": {
            "quantum_attack_applicability": 10,
            "standardization": 18,
            "implementation_readiness": 20,
            "migration_compatibility": 20,
        },
    },
    "HYBRID": {
        "score": 72,
        "vulnerable": False,
        "problem": "Combination of ECDLP (classical) and MLWE/Module-SIS (lattice)",
        "threat": (
            "The ECDSA component is quantum-vulnerable, but the ML-DSA component "
            "provides post-quantum security. An attacker must break both components. "
            "This provides transitional protection during migration."
        ),
        "recommendation": (
            "Hybrid mode provides good quantum-readiness. Consider completing "
            "migration to full ML-DSA for maximum post-quantum security."
        ),
        "breakdown": {
            "quantum_attack_applicability": 32,
            "standardization": 18,
            "implementation_readiness": 14,
            "migration_compatibility": 8,
        },
    },
    "ML-DSA": {
        "score": 92,
        "vulnerable": False,
        "problem": "Module Learning With Errors (MLWE) / Module Short Integer Solution (Module-SIS)",
        "threat": (
            "No known quantum algorithm efficiently solves MLWE or Module-SIS. "
            "ML-DSA is a NIST-standardized post-quantum signature scheme (FIPS 204). "
            "Security is based on well-studied lattice assumptions."
        ),
        "recommendation": (
            "ML-DSA provides strong post-quantum security. No immediate "
            "cryptographic migration is required. Monitor NIST updates for "
            "any changes to lattice-based security assumptions."
        ),
        "breakdown": {
            "quantum_attack_applicability": 40,
            "standardization": 20,
            "implementation_readiness": 18,
            "migration_compatibility": 14,
        },
    },
}

_DISCLAIMER = (
    "This quantum-readiness assessment is based on known cryptographic assumptions "
    "and published threat models (NIST PQC standardization, academic research on "
    "quantum algorithms). It does not constitute proof of resistance against unknown "
    "future quantum algorithms or mathematical breakthroughs. Security assessments "
    "should be reviewed periodically as the field of quantum computing evolves."
)


def analyze_quantum_readiness(algorithm: str) -> QuantumAssessment:
    algo_key = algorithm.upper().replace("-", "-")
    if algo_key == "MLDSA":
        algo_key = "ML-DSA"

    assessment = _ALGORITHM_ASSESSMENTS.get(algo_key)
    if not assessment:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    return QuantumAssessment(
        algorithm=algo_key,
        quantum_readiness_score=assessment["score"],
        is_vulnerable=assessment["vulnerable"],
        underlying_problem=assessment["problem"],
        quantum_threat=assessment["threat"],
        recommendation=assessment["recommendation"],
        disclaimer=_DISCLAIMER,
    )


def get_score_breakdown(algorithm: str) -> dict:
    algo_key = algorithm.upper().replace("-", "-")
    if algo_key == "MLDSA":
        algo_key = "ML-DSA"
    assessment = _ALGORITHM_ASSESSMENTS.get(algo_key)
    if not assessment:
        return {}
    return assessment["breakdown"]


def get_all_assessments() -> dict[str, QuantumAssessment]:
    return {algo: analyze_quantum_readiness(algo) for algo in _ALGORITHM_ASSESSMENTS}
