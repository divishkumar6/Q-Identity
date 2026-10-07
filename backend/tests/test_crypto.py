import pytest
from app.crypto import get_crypto_provider, get_supported_algorithms
from app.crypto.base import ICryptoProvider, KeyPair, SignatureResult
from app.core.security import (
    hash_password, verify_password, create_access_token,
    decode_access_token, generate_challenge, compute_hash,
    compute_identity_hash, generate_did,
)
from app.quantum.analyzer import analyze_quantum_readiness, get_score_breakdown, get_all_assessments


class TestPasswordSecurity:
    def test_hash_and_verify(self):
        h = hash_password("mypassword")
        assert verify_password("mypassword", h) is True

    def test_wrong_password(self):
        h = hash_password("mypassword")
        assert verify_password("wrongpassword", h) is False

    def test_different_hashes(self):
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2

    def test_empty_password(self):
        h = hash_password("")
        assert verify_password("", h) is True


class TestJWT:
    def test_create_and_decode(self):
        token = create_access_token({"sub": "user1", "role": "admin"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user1"

    def test_invalid_token(self):
        payload = decode_access_token("invalid.token.here")
        assert payload is None


class TestChallenge:
    def test_generate_challenge(self):
        ch = generate_challenge()
        assert len(ch) == 64

    def test_unique_challenges(self):
        ch1 = generate_challenge()
        ch2 = generate_challenge()
        assert ch1 != ch2


class TestHashing:
    def test_compute_hash(self):
        h = compute_hash("test data")
        assert len(h) == 64

    def test_deterministic(self):
        h1 = compute_hash("same input")
        h2 = compute_hash("same input")
        assert h1 == h2

    def test_identity_hash(self):
        h = compute_identity_hash("did:123", "pubkey", "ECDSA")
        assert len(h) == 64


class TestDID:
    def test_generate_did(self):
        did = generate_did()
        assert did.startswith("did:qidentity:")
        assert len(did) >= 30

    def test_unique_dids(self):
        d1 = generate_did()
        d2 = generate_did()
        assert d1 != d2


class TestCryptoProviders:
    def test_supported_algorithms(self):
        algos = get_supported_algorithms()
        assert "ECDSA" in algos
        assert "HYBRID" in algos
        assert "ML-DSA" in algos

    def test_ecdsa_provider(self):
        p = get_crypto_provider("ECDSA")
        assert isinstance(p, ICryptoProvider)
        assert p.get_algorithm_name() == "ECDSA"

    def test_mldsa_provider(self):
        p = get_crypto_provider("ML-DSA")
        assert isinstance(p, ICryptoProvider)
        assert p.get_algorithm_name() == "ML-DSA"

    def test_hybrid_provider(self):
        p = get_crypto_provider("HYBRID")
        assert isinstance(p, ICryptoProvider)
        assert p.get_algorithm_name() == "HYBRID"

    def test_invalid_provider(self):
        with pytest.raises(ValueError):
            get_crypto_provider("INVALID")


class TestQuantumAnalyzer:
    def test_ecdsa_assessment(self):
        a = analyze_quantum_readiness("ECDSA")
        assert a.quantum_readiness_score == 32
        assert a.is_vulnerable is True
        assert "Shor" in a.quantum_threat

    def test_mldsa_assessment(self):
        a = analyze_quantum_readiness("ML-DSA")
        assert a.quantum_readiness_score == 92
        assert a.is_vulnerable is False

    def test_hybrid_assessment(self):
        a = analyze_quantum_readiness("HYBRID")
        assert a.quantum_readiness_score == 72
        assert a.is_vulnerable is False

    def test_all_assessments(self):
        all_a = get_all_assessments()
        assert len(all_a) == 3
        assert "ECDSA" in all_a
        assert "ML-DSA" in all_a

    def test_score_breakdown(self):
        b = get_score_breakdown("ECDSA")
        assert "quantum_attack_applicability" in b
        assert "standardization" in b
        assert "implementation_readiness" in b
        assert "migration_compatibility" in b
        assert all(isinstance(v, int) for v in b.values())

    def test_disclaimer_present(self):
        a = analyze_quantum_readiness("ECDSA")
        assert "does not constitute proof" in a.disclaimer
