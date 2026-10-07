from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class AlgorithmChoice(str, Enum):
    ECDSA = "ECDSA"
    HYBRID = "HYBRID"
    MLDSA = "ML-DSA"


class IdentityStatusEnum(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    MIGRATED = "migrated"


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    organization: Optional[str] = None
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    organization: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class IdentityCreate(BaseModel):
    user_id: int
    algorithm: AlgorithmChoice = AlgorithmChoice.ECDSA


class IdentityResponse(BaseModel):
    id: int
    did: str
    user_id: int
    status: str
    algorithm: str
    public_key: str
    identity_hash: str
    blockchain_tx_hash: Optional[str]
    blockchain_block_number: Optional[int]
    security_level: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_migration_at: Optional[datetime]

    class Config:
        from_attributes = True


class AuthRequest(BaseModel):
    did: str
    signature: str


class AuthChallengeResponse(BaseModel):
    challenge: str
    expires_at: datetime


class AuthResult(BaseModel):
    verified: bool
    did: str
    algorithm: str
    identity_status: str
    blockchain_verified: bool
    message: str


class MigrationRequest(BaseModel):
    did: str
    target_algorithm: AlgorithmChoice


class MigrationStepResponse(BaseModel):
    step: int
    description: str
    status: str
    detail: Optional[str] = None


class MigrationResponse(BaseModel):
    did: str
    old_algorithm: str
    new_algorithm: str
    steps: list[MigrationStepResponse]
    completed: bool


class RevokeRequest(BaseModel):
    did: str
    reason: Optional[str] = None


class QuantumAssessmentResponse(BaseModel):
    algorithm: str
    quantum_readiness_score: float
    is_vulnerable: bool
    underlying_problem: str
    quantum_threat: str
    recommendation: str
    disclaimer: str


class BenchmarkRequest(BaseModel):
    algorithm: Optional[AlgorithmChoice] = None
    iterations: int = Field(default=100, ge=10, le=5000)
    operations: list[str] = Field(
        default=["keygen", "sign", "verify"],
    )


class BenchmarkResultResponse(BaseModel):
    algorithm: str
    operation: str
    iterations: int
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    median_time_ms: float
    std_dev_ms: float
    avg_signature_size: Optional[int]
    avg_key_size: Optional[int]


class BlockchainTxResponse(BaseModel):
    tx_hash: str
    block_number: Optional[int]
    identity_did: Optional[str]
    event_type: str
    payload_hash: Optional[str]
    gas_used: Optional[int]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TamperCheckResult(BaseModel):
    original_hash: str
    current_hash: str
    integrity_valid: bool
    signature_valid: Optional[bool]
    message: str


class ResearchSummary(BaseModel):
    total_identities: int
    active_identities: int
    revoked_identities: int
    migrated_identities: int
    pqc_identities: int
    hybrid_identities: int
    classical_identities: int
    total_transactions: int
    avg_auth_time_ms: Optional[float]
    avg_verify_time_ms: Optional[float]


class DemoStep(BaseModel):
    step: int
    total: int
    title: str
    status: str
    detail: Optional[str] = None
