from sqlalchemy import (
    Column, String, Integer, Text, DateTime, Boolean, Float, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.core.database import Base


class IdentityStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    MIGRATED = "migrated"


class CryptoAlgorithm(str, enum.Enum):
    ECDSA = "ECDSA"
    HYBRID = "HYBRID"
    MLDSA = "ML-DSA"


class MigrationStepStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    organization = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    identities = relationship("Identity", back_populates="user")


class Identity(Base):
    __tablename__ = "identities"

    id = Column(Integer, primary_key=True, index=True)
    did = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(IdentityStatus), default=IdentityStatus.ACTIVE)
    algorithm = Column(SAEnum(CryptoAlgorithm), default=CryptoAlgorithm.ECDSA)
    public_key = Column(Text, nullable=False)
    identity_hash = Column(String(255), nullable=False)
    blockchain_tx_hash = Column(String(255), nullable=True)
    blockchain_block_number = Column(Integer, nullable=True)
    security_level = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_migration_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="identities")
    keys = relationship("IdentityKey", back_populates="identity")
    migrations = relationship("MigrationEvent", back_populates="identity")
    auth_challenges = relationship("AuthenticationChallenge", back_populates="identity")


class IdentityKey(Base):
    __tablename__ = "identity_keys"

    id = Column(Integer, primary_key=True, index=True)
    identity_id = Column(Integer, ForeignKey("identities.id"), nullable=False)
    algorithm = Column(SAEnum(CryptoAlgorithm), nullable=False)
    public_key = Column(Text, nullable=False)
    private_key_ref = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    identity = relationship("Identity", back_populates="keys")


class AuthenticationChallenge(Base):
    __tablename__ = "authentication_challenges"

    id = Column(Integer, primary_key=True, index=True)
    identity_id = Column(Integer, ForeignKey("identities.id"), nullable=False)
    challenge = Column(String(255), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)

    identity = relationship("Identity", back_populates="auth_challenges")


class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(255), unique=True, index=True, nullable=False)
    block_number = Column(Integer, nullable=True)
    identity_did = Column(String(255), index=True, nullable=True)
    event_type = Column(String(100), nullable=False)
    payload_hash = Column(String(255), nullable=True)
    gas_used = Column(Integer, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class MigrationEvent(Base):
    __tablename__ = "migration_events"

    id = Column(Integer, primary_key=True, index=True)
    identity_id = Column(Integer, ForeignKey("identities.id"), nullable=False)
    old_algorithm = Column(SAEnum(CryptoAlgorithm), nullable=False)
    new_algorithm = Column(SAEnum(CryptoAlgorithm), nullable=False)
    old_public_key_ref = Column(String(255), nullable=True)
    new_public_key_ref = Column(String(255), nullable=True)
    blockchain_tx_hash = Column(String(255), nullable=True)
    step_status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    identity = relationship("Identity", back_populates="migrations")


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id = Column(Integer, primary_key=True, index=True)
    algorithm = Column(SAEnum(CryptoAlgorithm), nullable=False)
    iterations = Column(Integer, nullable=False)
    operation = Column(String(100), nullable=False)
    avg_time_ms = Column(Float, nullable=True)
    min_time_ms = Column(Float, nullable=True)
    max_time_ms = Column(Float, nullable=True)
    median_time_ms = Column(Float, nullable=True)
    std_dev_ms = Column(Float, nullable=True)
    avg_signature_size = Column(Integer, nullable=True)
    avg_key_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class QuantumAssessment(Base):
    __tablename__ = "quantum_assessments"

    id = Column(Integer, primary_key=True, index=True)
    identity_id = Column(Integer, ForeignKey("identities.id"), nullable=True)
    algorithm = Column(SAEnum(CryptoAlgorithm), nullable=False)
    quantum_readiness_score = Column(Float, nullable=False)
    is_vulnerable = Column(Boolean, nullable=False)
    assessment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RevocationEvent(Base):
    __tablename__ = "revocation_events"

    id = Column(Integer, primary_key=True, index=True)
    identity_id = Column(Integer, ForeignKey("identities.id"), nullable=False)
    reason = Column(String(500), nullable=True)
    blockchain_tx_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
