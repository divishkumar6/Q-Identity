from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import (
    Identity, IdentityKey, User, AuthenticationChallenge,
    BlockchainTransaction, MigrationEvent, IdentityStatus, CryptoAlgorithm
)
from app.crypto import get_crypto_provider
from app.blockchain.service import blockchain_service
from app.core.security import generate_did, compute_identity_hash, generate_challenge
from app.core.config import get_settings

settings = get_settings()


class IdentityService:
    """Core identity management service."""

    def create_identity(self, db: Session, user_id: int, algorithm: str = "ECDSA") -> dict:
        provider = get_crypto_provider(algorithm)
        keypair = provider.generate_keypair()

        did = generate_did()
        identity_hash = compute_identity_hash(did, keypair.public_key.hex(), algorithm)

        # Create identity
        algo_enum = {"ECDSA": CryptoAlgorithm.ECDSA, "HYBRID": CryptoAlgorithm.HYBRID, "ML-DSA": CryptoAlgorithm.MLDSA}
        identity = Identity(
            did=did,
            user_id=user_id,
            status=IdentityStatus.ACTIVE,
            algorithm=algo_enum.get(algorithm, CryptoAlgorithm.ECDSA),
            public_key=keypair.public_key.hex(),
            identity_hash=identity_hash,
            security_level=keypair.security_level,
        )
        db.add(identity)
        db.flush()

        # Store key reference
        key_record = IdentityKey(
            identity_id=identity.id,
            algorithm=algo_enum.get(algorithm, CryptoAlgorithm.ECDSA),
            public_key=keypair.public_key.hex(),
            private_key_ref=keypair.private_key.hex(),
            is_active=True,
        )
        db.add(key_record)

        # Record on blockchain
        tx_result = blockchain_service.register_identity(
            did, keypair.public_key, identity_hash, algorithm
        )

        if tx_result:
            identity.blockchain_tx_hash = tx_result.get("tx_hash")
            identity.blockchain_block_number = tx_result.get("block_number")

            blockchain_tx = BlockchainTransaction(
                tx_hash=tx_result["tx_hash"],
                block_number=tx_result.get("block_number"),
                identity_did=did,
                event_type="identity_registered",
                payload_hash=identity_hash,
                gas_used=tx_result.get("gas_used"),
                status=tx_result.get("status", "confirmed"),
            )
            db.add(blockchain_tx)

        db.commit()
        db.refresh(identity)

        return {
            "id": identity.id,
            "did": did,
            "algorithm": algorithm,
            "public_key": keypair.public_key.hex(),
            "private_key_ref": keypair.private_key.hex(),  # For demo only
            "identity_hash": identity_hash,
            "status": identity.status.value,
            "blockchain_tx": tx_result,
            "security_level": keypair.security_level,
            "created_at": identity.created_at.isoformat(),
        }

    def get_identity(self, db: Session, did: str) -> Optional[dict]:
        identity = db.query(Identity).filter(Identity.did == did).first()
        if not identity:
            return None
        return {
            "id": identity.id,
            "did": identity.did,
            "user_id": identity.user_id,
            "status": identity.status.value,
            "algorithm": identity.algorithm.value,
            "public_key": identity.public_key,
            "identity_hash": identity.identity_hash,
            "blockchain_tx_hash": identity.blockchain_tx_hash,
            "blockchain_block_number": identity.blockchain_block_number,
            "security_level": identity.security_level,
            "created_at": identity.created_at.isoformat(),
            "updated_at": identity.updated_at.isoformat(),
            "last_migration_at": identity.last_migration_at.isoformat() if identity.last_migration_at else None,
        }

    def list_identities(self, db: Session, user_id: Optional[int] = None, limit: int = 50) -> list[dict]:
        query = db.query(Identity)
        if user_id:
            query = query.filter(Identity.user_id == user_id)
        identities = query.order_by(Identity.id.desc()).limit(limit).all()
        return [
            {
                "id": i.id,
                "did": i.did,
                "status": i.status.value,
                "algorithm": i.algorithm.value,
                "identity_hash": i.identity_hash,
                "created_at": i.created_at.isoformat(),
            }
            for i in identities
        ]

    def create_challenge(self, db: Session, did: str) -> Optional[dict]:
        identity = db.query(Identity).filter(Identity.did == did).first()
        if not identity or identity.status != IdentityStatus.ACTIVE:
            return None

        challenge = generate_challenge()
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.CHALLENGE_EXPIRATION_SECONDS)

        auth_challenge = AuthenticationChallenge(
            identity_id=identity.id,
            challenge=challenge,
            expires_at=expires_at,
        )
        db.add(auth_challenge)
        db.commit()

        return {"challenge": challenge, "expires_at": expires_at.isoformat()}

    def verify_authentication(self, db: Session, did: str, signature_hex: str) -> dict:
        identity = db.query(Identity).filter(Identity.did == did).first()
        if not identity:
            return {"verified": False, "message": "Identity not found", "identity_status": "unknown"}

        if identity.status == IdentityStatus.REVOKED:
            return {"verified": False, "message": "Identity is revoked", "identity_status": "revoked"}

        if identity.status != IdentityStatus.ACTIVE:
            return {"verified": False, "message": f"Identity status: {identity.status.value}", "identity_status": identity.status.value}

        # Get latest unused challenge
        challenge_record = (
            db.query(AuthenticationChallenge)
            .filter(
                AuthenticationChallenge.identity_id == identity.id,
                AuthenticationChallenge.is_used == False,
            )
            .order_by(AuthenticationChallenge.id.desc())
            .first()
        )

        if not challenge_record:
            return {"verified": False, "message": "No active challenge found", "identity_status": identity.status.value}

        if challenge_record.expires_at.replace(tzinfo=None) < datetime.now(timezone.utc).replace(tzinfo=None):
            return {"verified": False, "message": "Challenge expired", "identity_status": identity.status.value}

        challenge_record.is_used = True

        # Verify signature
        provider = get_crypto_provider(identity.algorithm.value)
        try:
            message = challenge_record.challenge.encode()
            signature = bytes.fromhex(signature_hex)
            public_key = bytes.fromhex(identity.public_key)
            valid = provider.verify(public_key, message, signature)
        except Exception as e:
            db.commit()
            return {"verified": False, "message": f"Signature verification error: {str(e)}", "identity_status": identity.status.value}

        db.commit()

        if valid:
            return {
                "verified": True,
                "message": "Identity verified",
                "identity_status": identity.status.value,
                "algorithm": identity.algorithm.value,
                "blockchain_verified": bool(identity.blockchain_tx_hash),
            }
        else:
            return {"verified": False, "message": "Invalid signature", "identity_status": identity.status.value}

    def revoke_identity(self, db: Session, did: str, reason: str = None) -> Optional[dict]:
        identity = db.query(Identity).filter(Identity.did == did).first()
        if not identity:
            return None

        identity.status = IdentityStatus.REVOKED

        tx_result = blockchain_service.revoke_identity(did)

        blockchain_tx = None
        if tx_result:
            blockchain_tx = BlockchainTransaction(
                tx_hash=tx_result["tx_hash"],
                block_number=tx_result.get("block_number"),
                identity_did=did,
                event_type="identity_revoked",
                gas_used=tx_result.get("gas_used"),
                status=tx_result.get("status", "confirmed"),
            )
            db.add(blockchain_tx)

        db.commit()
        return {
            "did": did,
            "status": "revoked",
            "reason": reason,
            "blockchain_tx": tx_result,
        }


identity_service = IdentityService()
