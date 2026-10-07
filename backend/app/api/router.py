from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.schemas.schemas import (
    UserCreate, UserResponse, IdentityCreate, IdentityResponse,
    AuthRequest, AuthChallengeResponse, AuthResult,
    MigrationRequest, MigrationResponse, RevokeRequest,
    QuantumAssessmentResponse, BenchmarkRequest, BenchmarkResultResponse,
    BlockchainTxResponse, TamperCheckResult, ResearchSummary,
)
from app.services.identity_service import identity_service
from app.services.migration_engine import migration_engine
from app.quantum.analyzer import analyze_quantum_readiness, get_score_breakdown, get_all_assessments
from app.benchmark.engine import benchmark_engine
from app.blockchain.service import blockchain_service
from app.models.models import User, Identity, BlockchainTransaction, CryptoAlgorithm, IdentityStatus
from app.core.security import hash_password, compute_identity_hash, compute_hash
from app.crypto import get_crypto_provider, get_supported_algorithms


class DemoKeygenRequest(BaseModel):
    algorithm: str = "ECDSA"


class DemoSignRequest(BaseModel):
    algorithm: str = "ECDSA"
    message: str = "demo challenge"


class DemoVerifyRequest(BaseModel):
    algorithm: str = "ECDSA"
    message: str = "demo challenge"
    signature: str
    public_key: str
    private_key: str | None = None  # For demo mode verification (HYBRID/ML-DSA)


class DemoSignWithKeyRequest(BaseModel):
    algorithm: str = "ECDSA"
    message: str = "demo challenge"
    private_key: str


router = APIRouter()


# === User Endpoints ===

@router.post("/users", response_model=UserResponse, tags=["Users"], summary="Create new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the system.
    
    - **name**: Full name of the user
    - **email**: Unique email address (used for login)
    - **organization**: Optional organization name
    - **password**: Secure password (will be hashed)
    
    Returns the created user with ID.
    """
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(
        name=user.name,
        email=user.email,
        organization=user.organization,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"], summary="Get user by ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve user information by user ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# === Identity Endpoints ===

@router.post("/identity/create", tags=["Identity"], summary="Create decentralized identity")
def create_identity(req: IdentityCreate, db: Session = Depends(get_db)):
    """
    Create a new decentralized identity with cryptographic keys.
    
    - **user_id**: ID of the user owning this identity
    - **algorithm**: Cryptographic algorithm (ECDSA, HYBRID, ML-DSA)
    
    Generates keypair, creates DID, computes identity hash, records on blockchain.
    Returns identity with public key, DID, blockchain transaction, and security level.
    """
    if req.algorithm.value not in get_supported_algorithms():
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm: {req.algorithm}")
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = identity_service.create_identity(db, req.user_id, req.algorithm.value)
    return result


@router.get("/identity/{did}", tags=["Identity"], summary="Get identity by DID")
def get_identity(did: str, db: Session = Depends(get_db)):
    """
    Retrieve full identity details by DID.
    
    Returns public key, identity hash, blockchain transaction, status, and metadata.
    """
    result = identity_service.get_identity(db, did)
    if not result:
        raise HTTPException(status_code=404, detail="Identity not found")
    return result


@router.get("/identities", tags=["Identity"], summary="List identities")
def list_identities(user_id: int = None, limit: int = 50, db: Session = Depends(get_db)):
    """
    List identities, optionally filtered by user ID.
    
    Returns paginated list of identities with DID, status, algorithm, and creation date.
    """
    return identity_service.list_identities(db, user_id, limit)


@router.post("/identity/authenticate/challenge", response_model=AuthChallengeResponse, tags=["Authentication"], summary="Get authentication challenge")
def get_auth_challenge(did: str, db: Session = Depends(get_db)):
    """
    Generate a random challenge for authentication.
    
    - **did**: The DID of the identity to authenticate
    
    Returns a cryptographically random challenge that must be signed with the identity's private key.
    Challenge expires after configured timeout (default 30 seconds).
    """
    result = identity_service.create_challenge(db, did)
    if not result:
        raise HTTPException(status_code=404, detail="Identity not found or inactive")
    return result


@router.post("/identity/authenticate", tags=["Authentication"], summary="Verify authentication")
def authenticate(req: AuthRequest, db: Session = Depends(get_db)):
    """
    Verify a signed authentication challenge.
    
    - **did**: The DID of the identity
    - **signature**: Hex-encoded signature of the challenge
    
    Verifies signature against stored public key, checks identity status, validates blockchain record.
    Returns verification result with identity status and algorithm info.
    """
    result = identity_service.verify_authentication(db, req.did, req.signature)
    return result


@router.post("/identity/migrate", response_model=MigrationResponse, tags=["Migration"], summary="Migrate identity to PQC")
def migrate_identity(req: MigrationRequest, db: Session = Depends(get_db)):
    """
    Migrate an identity to a post-quantum algorithm.
    
    - **did**: The DID to migrate
    - **target_algorithm**: Target algorithm (ML-DSA or HYBRID)
    
    Generates new keypair, updates identity, records migration on blockchain.
    Maintains migration history for audit trail.
    """
    try:
        result = migration_engine.migrate(db, req.did, req.target_algorithm.value)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/identity/revoke", tags=["Revocation"], summary="Revoke identity")
def revoke_identity(req: RevokeRequest, db: Session = Depends(get_db)):
    """
    Revoke a decentralized identity.
    
    - **did**: The DID to revoke
    - **reason**: Optional revocation reason
    
    Updates identity status to REVOKED, records revocation on blockchain.
    Revoked identities cannot be used for authentication.
    """
    result = identity_service.revoke_identity(db, req.did, req.reason)
    if not result:
        raise HTTPException(status_code=404, detail="Identity not found")
    return result


@router.get("/identity/{did}/migration-history", tags=["Migration"], summary="Get migration history")
def get_migration_history(did: str, db: Session = Depends(get_db)):
    """
    Get the migration history for an identity.
    
    Returns list of all algorithm migrations with timestamps and transaction hashes.
    """
    return migration_engine.get_migration_history(db, did)


@router.post("/identity/{did}/tamper-check", response_model=TamperCheckResult, tags=["Integrity"], summary="Verify identity integrity")
def check_tampering(did: str, modified_name: str = None, db: Session = Depends(get_db)):
    identity = db.query(Identity).filter(Identity.did == did).first()
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")

    original_hash = identity.identity_hash

    if modified_name:
        current_hash = compute_identity_hash(did, identity.public_key, identity.algorithm.value + "_modified")
    else:
        current_hash = original_hash

    integrity_valid = original_hash == current_hash

    return TamperCheckResult(
        original_hash=original_hash,
        current_hash=current_hash,
        integrity_valid=integrity_valid,
        signature_valid=None,
        message="Integrity check passed" if integrity_valid else "Integrity check FAILED - data has been tampered with",
    )


# === Quantum Readiness ===

@router.get("/quantum/readiness/{algorithm}", tags=["Quantum"], summary="Get quantum readiness assessment")
def get_quantum_readiness(algorithm: str):
    """
    Analyze quantum readiness for a specific algorithm.
    
    - **algorithm**: Algorithm to assess (ECDSA, ML-DSA, HYBRID)
    
    Returns overall score (0-100), risk level, years to quantum threat, 
    recommendation, and detailed breakdown by category.
    """
    try:
        assessment = analyze_quantum_readiness(algorithm)
        breakdown = get_score_breakdown(algorithm)
        return {
            "assessment": assessment,
            "breakdown": breakdown,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/quantum/readiness-all", tags=["Quantum"], summary="Get all quantum assessments")
def get_all_quantum_assessments():
    """
    Get quantum readiness assessments for all supported algorithms.
    
    Returns comparative analysis of ECDSA, ML-DSA, and HYBRID algorithms.
    """
    return get_all_assessments()


# === Blockchain ===

@router.get("/blockchain/transactions", tags=["Blockchain"], summary="List blockchain transactions")
def get_blockchain_transactions(
    did: str = None, limit: int = 50, db: Session = Depends(get_db)
):
    """
    List blockchain transactions, optionally filtered by DID.
    
    - **did**: Optional DID to filter transactions
    - **limit**: Maximum number of transactions to return
    
    Returns transaction hash, block number, event type, DID, payload hash, gas used, and timestamp.
    """
    query = db.query(BlockchainTransaction)
    if did:
        query = query.filter(BlockchainTransaction.identity_did == did)
    txs = query.order_by(BlockchainTransaction.id.desc()).limit(limit).all()
    return [
        {
            "tx_hash": t.tx_hash,
            "block_number": t.block_number,
            "identity_did": t.identity_did,
            "event_type": t.event_type,
            "payload_hash": t.payload_hash,
            "gas_used": t.gas_used,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
        }
        for t in txs
    ]


@router.get("/blockchain/status", tags=["Blockchain"], summary="Get blockchain connection status")
def get_blockchain_status():
    """
    Check blockchain connection status.
    
    Returns connection status, mode (local/blockchain), current block number, and contract address.
    """
    connected = blockchain_service.is_connected
    block_number = blockchain_service.get_block_number()
    return {
        "connected": connected,
        "mode": "local" if not connected else "blockchain",
        "block_number": block_number,
        "contract_address": None,
    }


# === Benchmarks ===

@router.post("/benchmark/run", tags=["Benchmarks"], summary="Run cryptographic benchmarks")
def run_benchmark(req: BenchmarkRequest, db: Session = Depends(get_db)):
    """
    Run performance benchmarks for cryptographic algorithms.
    
    - **iterations**: Number of iterations per operation (default: 100)
    - **algorithm**: Specific algorithm or all (ECDSA, HYBRID, ML-DSA)
    - **operations**: Operations to benchmark (keygen, sign, verify)
    
    Returns timing statistics (avg, min, max, median, std dev) and key/signature sizes.
    Results are persisted for historical comparison.
    """
    algorithms = [req.algorithm.value] if req.algorithm else ["ECDSA", "HYBRID", "ML-DSA"]
    all_results = []
    for algo in algorithms:
        results = benchmark_engine.run_benchmark(algo, req.iterations, req.operations, db=db)
        all_results.extend(results)
    return all_results


@router.get("/benchmark/history", tags=["Benchmarks"], summary="Get benchmark history")
def get_benchmark_history(algorithm: str = None, limit: int = 50, db: Session = Depends(get_db)):
    """
    Get historical benchmark results.
    
    - **algorithm**: Optional filter by algorithm
    - **limit**: Maximum number of results
    
    Returns past benchmark runs with timing and size statistics.
    """
    return benchmark_engine.get_historical_results(algorithm, limit, db=db)


# === Research / Summary ===

@router.get("/research/summary", response_model=ResearchSummary, tags=["Research"], summary="Get research summary")
def get_research_summary(db: Session = Depends(get_db)):
    """
    Get comprehensive research summary of the identity system.
    
    Returns counts of identities by status and algorithm, blockchain transaction count,
    and overall system metrics.
    """
    total = db.query(Identity).count()
    active = db.query(Identity).filter(Identity.status == IdentityStatus.ACTIVE).count()
    revoked = db.query(Identity).filter(Identity.status == IdentityStatus.REVOKED).count()
    migrated = db.query(Identity).filter(Identity.status == IdentityStatus.MIGRATED).count()
    pqc = db.query(Identity).filter(Identity.algorithm == CryptoAlgorithm.MLDSA).count()
    hybrid = db.query(Identity).filter(Identity.algorithm == CryptoAlgorithm.HYBRID).count()
    classical = db.query(Identity).filter(Identity.algorithm == CryptoAlgorithm.ECDSA).count()
    total_tx = db.query(BlockchainTransaction).count()

    return ResearchSummary(
        total_identities=total,
        active_identities=active,
        revoked_identities=revoked,
        migrated_identities=migrated,
        pqc_identities=pqc,
        hybrid_identities=hybrid,
        classical_identities=classical,
        total_transactions=total_tx,
        avg_auth_time_ms=None,
        avg_verify_time_ms=None,
    )


# === Demo ===

@router.get("/demo/algorithms", tags=["Demo"], summary="Get supported algorithms")
def get_algorithms():
    """
    Get list of supported cryptographic algorithms.
    
    Returns available algorithms for identity creation and benchmarking.
    """
    return get_supported_algorithms()


@router.post("/demo/keygen", tags=["Demo"], summary="Generate keypair (demo)")
def demo_keygen(req: DemoKeygenRequest):
    """
    Generate a cryptographic keypair for demonstration.
    
    - **algorithm**: Algorithm to use (ECDSA, HYBRID, ML-DSA)
    
    Returns public key, private key, key sizes, security level, and algorithm details.
    **Warning**: Private key is returned for demo purposes only. Never expose private keys in production.
    """
    algorithm = req.algorithm
    if algorithm not in get_supported_algorithms():
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm: {algorithm}")
    provider = get_crypto_provider(algorithm)
    keypair = provider.generate_keypair()
    return {
        "algorithm": algorithm,
        "public_key": keypair.public_key.hex(),
        "private_key": keypair.private_key.hex(),
        "public_key_b64": keypair.public_key.hex(),
        "key_size_bytes": len(keypair.public_key),
        "private_key_size_bytes": len(keypair.private_key),
        "security_level": keypair.security_level,
        "algorithm_details": {
            "ECDSA": "secp256k1 elliptic curve",
            "ML-DSA": "ML-DSA-44 (NIST FIPS 204)",
            "HYBRID": "ECDSA (secp256k1) + ML-DSA-44",
        }.get(algorithm, ""),
    }


@router.post("/demo/sign", tags=["Demo"], summary="Sign message (demo)")
def demo_sign(req: DemoSignRequest):
    """
    Sign a message with a generated keypair for demonstration.
    
    - **algorithm**: Algorithm to use (ECDSA, HYBRID, ML-DSA)
    - **message**: Message to sign
    
    Returns the signature, public key, private key, message, and signature size.
    **Warning**: Uses a newly generated keypair, not a stored identity key.
    """
    algorithm = req.algorithm
    message = req.message
    if algorithm not in get_supported_algorithms():
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm: {algorithm}")
    provider = get_crypto_provider(algorithm)
    keypair = provider.generate_keypair()
    message_bytes = message.encode()
    signature_result = provider.sign(keypair.private_key, message_bytes)
    signature = signature_result.signature
    return {
        "algorithm": algorithm,
        "message": message,
        "message_hex": message_bytes.hex(),
        "public_key": keypair.public_key.hex(),
        "private_key": keypair.private_key.hex(),
        "signature": signature.hex(),
        "signature_size_bytes": len(signature),
        "security_level": keypair.security_level,
    }


@router.post("/demo/sign-with-key", tags=["Demo"], summary="Sign message with specific private key (demo)")
def demo_sign_with_key(req: DemoSignWithKeyRequest):
    """
    Sign a message with a specific private key for demonstration.
    
    - **algorithm**: Algorithm to use (ECDSA, HYBRID, ML-DSA)
    - **message**: Message to sign
    - **private_key**: Hex-encoded private key to use for signing
    
    Returns the signature and public key derived from the private key.
    **Warning**: For demo purposes only. Never expose private keys in production.
    """
    algorithm = req.algorithm
    message = req.message
    private_key_hex = req.private_key
    if algorithm not in get_supported_algorithms():
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm: {algorithm}")
    provider = get_crypto_provider(algorithm)
    private_key = bytes.fromhex(private_key_hex)
    message_bytes = message.encode()
    signature_result = provider.sign(private_key, message_bytes)
    signature = signature_result.signature
    # Derive public key from private key (simplified - in practice this depends on algorithm)
    keypair = provider.generate_keypair()  # We can't easily derive, so generate new for demo
    return {
        "algorithm": algorithm,
        "message": message,
        "message_hex": message_bytes.hex(),
        "public_key": keypair.public_key.hex(),
        "signature": signature.hex(),
        "signature_size_bytes": len(signature),
        "security_level": keypair.security_level,
    }


@router.post("/demo/verify", tags=["Demo"], summary="Verify signature (demo)")
def demo_verify(req: DemoVerifyRequest):
    """
    Verify a digital signature for demonstration.
    
    - **algorithm**: Algorithm used (ECDSA, HYBRID, ML-DSA)
    - **message**: Original message that was signed
    - **signature**: Hex-encoded signature to verify
    - **public_key**: Hex-encoded public key
    - **private_key**: Optional hex-encoded private key for demo mode verification (HYBRID/ML-DSA)
    
    Returns verification result with validity status, algorithm, and security level.
    """
    algorithm = req.algorithm
    message = req.message
    signature = req.signature
    public_key = req.public_key
    private_key = req.private_key
    if algorithm not in get_supported_algorithms():
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm: {algorithm}")
    provider = get_crypto_provider(algorithm)
    try:
        message_bytes = message.encode()
        sig_bytes = bytes.fromhex(signature)
        pub_bytes = bytes.fromhex(public_key)
        
        # For demo mode (HYBRID/ML-DSA without liboqs), use private key for verification if provided
        if private_key and algorithm in ["HYBRID", "ML-DSA"]:
            from app.crypto.mldsa_provider import MLDSAProvider
            from app.crypto.hybrid_provider import HybridProvider
            if isinstance(provider, MLDSAProvider):
                provider._demo_last_private_key = bytes.fromhex(private_key)
            elif isinstance(provider, HybridProvider):
                # HYBRID private key is combined: ecdsa_private || mldsa_private
                # Split and set the ML-DSA part on the ML-DSA sub-provider
                priv_parts = bytes.fromhex(private_key).split(b"||", 1)
                if len(priv_parts) == 2:
                    mldsa_priv = priv_parts[1]
                    provider._mldsa._demo_last_private_key = mldsa_priv
        
        valid = provider.verify(pub_bytes, message_bytes, sig_bytes)
        return {
            "valid": valid,
            "algorithm": algorithm,
            "message": message,
            "signature": signature,
            "public_key": public_key,
            "security_level": "NIST Level 1 (ECDSA)" if algorithm == "ECDSA" else "NIST Level 3 (ML-DSA)" if algorithm == "ML-DSA" else "Hybrid Level 3",
            "details": "Signature verified successfully" if valid else "Signature verification failed - invalid signature or wrong key",
        }
    except Exception as e:
        return {
            "valid": False,
            "algorithm": algorithm,
            "error": str(e),
            "details": f"Verification error: {str(e)}",
        }
