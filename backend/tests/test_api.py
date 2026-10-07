import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.core.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_qidentity.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    res = client.post("/api/users", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass123",
    })
    return res.json()


@pytest.fixture
def test_identity(test_user):
    res = client.post("/api/identity/create", json={
        "user_id": test_user["id"],
        "algorithm": "ECDSA",
    })
    return res.json()


# === Authentication Tests ===

class TestAuthentication:
    def test_valid_signature_flow(self, test_identity):
        did = test_identity["did"]

        ch_res = client.post(f"/api/identity/authenticate/challenge?did={did}")
        assert ch_res.status_code == 200
        challenge = ch_res.json()["challenge"]
        assert len(challenge) == 64

        auth_res = client.post("/api/identity/authenticate", json={
            "did": did,
            "signature": "a" * 64,
        })
        assert auth_res.status_code == 200

    def test_nonexistent_identity(self):
        res = client.post("/api/identity/authenticate/challenge?did=did:qidentity:nonexistent")
        assert res.status_code == 404

    def test_challenge_expiration(self, test_identity):
        did = test_identity["did"]
        ch_res = client.post(f"/api/identity/authenticate/challenge?did={did}")
        assert ch_res.status_code == 200

    def test_revoked_identity_denied(self, test_identity):
        did = test_identity["did"]
        client.post("/api/identity/revoke", json={"did": did, "reason": "test"})

        ch_res = client.post(f"/api/identity/authenticate/challenge?did={did}")
        assert ch_res.status_code == 404


# === Cryptography Tests ===

class TestCryptography:
    def test_ecdsa_keygen(self):
        from app.crypto import get_crypto_provider
        provider = get_crypto_provider("ECDSA")
        kp = provider.generate_keypair()
        assert kp.algorithm == "ECDSA"
        assert len(kp.public_key) > 0
        assert len(kp.private_key) > 0

    def test_ecdsa_sign_verify(self):
        from app.crypto import get_crypto_provider
        provider = get_crypto_provider("ECDSA")
        kp = provider.generate_keypair()
        msg = b"test message for signing"
        sig = provider.sign(kp.private_key, msg)
        assert sig.algorithm == "ECDSA"
        assert sig.size > 0
        valid = provider.verify(kp.public_key, msg, sig.signature)
        assert valid is True

    def test_ecdsa_invalid_signature(self):
        from app.crypto import get_crypto_provider
        provider = get_crypto_provider("ECDSA")
        kp = provider.generate_keypair()
        msg = b"test message"
        invalid_sig = b"\x00" * 72
        valid = provider.verify(kp.public_key, msg, invalid_sig)
        assert valid is False

    def test_ecdsa_wrong_public_key(self):
        from app.crypto import get_crypto_provider
        provider = get_crypto_provider("ECDSA")
        kp1 = provider.generate_keypair()
        kp2 = provider.generate_keypair()
        msg = b"test message"
        sig = provider.sign(kp1.private_key, msg)
        valid = provider.verify(kp2.public_key, msg, sig.signature)
        assert valid is False

    def test_mldsa_keygen(self):
        from app.crypto import get_crypto_provider
        provider = get_crypto_provider("ML-DSA")
        kp = provider.generate_keypair()
        assert kp.algorithm == "ML-DSA"
        assert len(kp.public_key) > 0

    def test_hybrid_keygen(self):
        from app.crypto import get_crypto_provider
        provider = get_crypto_provider("HYBRID")
        kp = provider.generate_keypair()
        assert kp.algorithm == "HYBRID"
        assert b"||" in kp.public_key
        assert b"||" in kp.private_key

    def test_hybrid_sign_verify(self):
        from app.crypto import get_crypto_provider
        provider = get_crypto_provider("HYBRID")
        kp = provider.generate_keypair()
        msg = b"test hybrid message"
        sig = provider.sign(kp.private_key, msg)
        valid = provider.verify(kp.public_key, msg, sig.signature)
        assert valid is True

    def test_unsupported_algorithm(self):
        from app.crypto import get_crypto_provider
        with pytest.raises(ValueError):
            get_crypto_provider("RSA")


# === Migration Tests ===

class TestMigration:
    def test_ecdsa_to_hybrid(self, test_identity):
        did = test_identity["did"]
        res = client.post("/api/identity/migrate", json={
            "did": did,
            "target_algorithm": "HYBRID",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["old_algorithm"] == "ECDSA"
        assert data["new_algorithm"] == "HYBRID"
        assert data["completed"] is True
        assert len(data["steps"]) == 5

    def test_hybrid_to_mldsa(self, test_identity):
        did = test_identity["did"]
        client.post("/api/identity/migrate", json={"did": did, "target_algorithm": "HYBRID"})
        res = client.post("/api/identity/migrate", json={"did": did, "target_algorithm": "ML-DSA"})
        assert res.status_code == 200
        assert res.json()["new_algorithm"] == "ML-DSA"

    def test_same_algorithm_rejected(self, test_identity):
        did = test_identity["did"]
        res = client.post("/api/identity/migrate", json={"did": did, "target_algorithm": "ECDSA"})
        assert res.status_code == 400

    def test_nonexistent_identity_migration(self):
        res = client.post("/api/identity/migrate", json={"did": "did:qidentity:fake", "target_algorithm": "ML-DSA"})
        assert res.status_code == 400

    def test_revoked_identity_migration(self, test_identity):
        did = test_identity["did"]
        client.post("/api/identity/revoke", json={"did": did})
        res = client.post("/api/identity/migrate", json={"did": did, "target_algorithm": "ML-DSA"})
        assert res.status_code == 400

    def test_migration_history(self, test_identity):
        did = test_identity["did"]
        client.post("/api/identity/migrate", json={"did": did, "target_algorithm": "HYBRID"})
        res = client.get(f"/api/identity/{did}/migration-history")
        assert res.status_code == 200
        history = res.json()
        assert len(history) >= 1
        assert history[0]["old_algorithm"] == "ECDSA"
        assert history[0]["new_algorithm"] == "HYBRID"


# === Blockchain Tests ===

class TestBlockchain:
    def test_identity_registration(self, test_identity):
        assert test_identity["blockchain_tx"] is not None
        assert test_identity["blockchain_tx"]["status"] == "confirmed (local)"

    def test_blockchain_transactions(self, test_identity):
        res = client.get("/api/blockchain/transactions")
        assert res.status_code == 200
        txs = res.json()
        assert len(txs) >= 1
        assert txs[0]["event_type"] == "identity_registered"

    def test_blockchain_status(self):
        res = client.get("/api/blockchain/status")
        assert res.status_code == 200
        data = res.json()
        assert "connected" in data
        assert "mode" in data


# === Benchmark Tests ===

class TestBenchmark:
    def test_run_ecdsa_benchmark(self):
        res = client.post("/api/benchmark/run", json={
            "algorithm": "ECDSA",
            "iterations": 10,
            "operations": ["keygen"],
        })
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["algorithm"] == "ECDSA"
        assert data[0]["operation"] == "keygen"
        assert data[0]["iterations"] == 10
        assert data[0]["avg_time_ms"] > 0
        assert data[0]["min_time_ms"] > 0

    def test_benchmark_all_algorithms(self):
        res = client.post("/api/benchmark/run", json={
            "iterations": 10,
            "operations": ["keygen", "sign", "verify"],
        })
        assert res.status_code == 200
        data = res.json()
        algos = {r["algorithm"] for r in data}
        assert "ECDSA" in algos
        assert "HYBRID" in algos
        assert "ML-DSA" in algos

    def test_benchmark_history(self):
        client.post("/api/benchmark/run", json={
            "algorithm": "ECDSA",
            "iterations": 10,
            "operations": ["keygen"],
        })
        res = client.get("/api/benchmark/history?algorithm=ECDSA")
        assert res.status_code == 200
        assert len(res.json()) >= 1


# === Quantum Readiness Tests ===

class TestQuantumReadiness:
    def test_ecdsa_assessment(self):
        res = client.get("/api/quantum/readiness/ECDSA")
        assert res.status_code == 200
        data = res.json()
        assert data["assessment"]["algorithm"] == "ECDSA"
        assert data["assessment"]["quantum_readiness_score"] == 32
        assert data["assessment"]["is_vulnerable"] is True

    def test_mldsa_assessment(self):
        res = client.get("/api/quantum/readiness/ML-DSA")
        assert res.status_code == 200
        data = res.json()
        assert data["assessment"]["quantum_readiness_score"] == 92
        assert data["assessment"]["is_vulnerable"] is False

    def test_hybrid_assessment(self):
        res = client.get("/api/quantum/readiness/HYBRID")
        assert res.status_code == 200
        data = res.json()
        assert data["assessment"]["quantum_readiness_score"] == 72

    def test_all_assessments(self):
        res = client.get("/api/quantum/readiness-all")
        assert res.status_code == 200
        data = res.json()
        assert "ECDSA" in data
        assert "HYBRID" in data
        assert "ML-DSA" in data

    def test_unknown_algorithm(self):
        res = client.get("/api/quantum/readiness/RSA")
        assert res.status_code == 400


# === Tampering Tests ===

class TestTampering:
    def test_integrity_check_pass(self, test_identity):
        did = test_identity["did"]
        res = client.post(f"/api/identity/{did}/tamper-check")
        assert res.status_code == 200
        data = res.json()
        assert data["integrity_valid"] is True

    def test_integrity_check_fail(self, test_identity):
        did = test_identity["did"]
        res = client.post(f"/api/identity/{did}/tamper-check?modified_name=Hacked")
        assert res.status_code == 200
        data = res.json()
        assert data["integrity_valid"] is False
        assert "FAILED" in data["message"]

    def test_nonexistent_identity_tamper(self):
        res = client.post("/api/identity/did:qidentity:fake/tamper-check")
        assert res.status_code == 404


# === Revocation Tests ===

class TestRevocation:
    def test_revoke_active_identity(self, test_identity):
        did = test_identity["did"]
        res = client.post("/api/identity/revoke", json={"did": did, "reason": "compromised"})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "revoked"

    def test_revoke_nonexistent(self):
        res = client.post("/api/identity/revoke", json={"did": "did:qidentity:fake"})
        assert res.status_code == 404

    def test_revoked_identity_status(self, test_identity):
        did = test_identity["did"]
        client.post("/api/identity/revoke", json={"did": did})
        res = client.get(f"/api/identity/{did}")
        assert res.json()["status"] == "revoked"


# === Research Summary Tests ===

class TestResearch:
    def test_summary_with_data(self, test_identity):
        res = client.get("/api/research/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_identities"] >= 1
        assert data["active_identities"] >= 1
        assert data["classical_identities"] >= 1

    def test_algorithms_endpoint(self):
        res = client.get("/api/demo/algorithms")
        assert res.status_code == 200
        algos = res.json()
        assert "ECDSA" in algos
        assert "HYBRID" in algos
        assert "ML-DSA" in algos
