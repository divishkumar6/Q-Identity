from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import (
    Identity, IdentityKey, MigrationEvent, BlockchainTransaction,
    IdentityStatus, CryptoAlgorithm
)
from app.crypto import get_crypto_provider
from app.blockchain.service import blockchain_service
from app.core.security import compute_identity_hash

_ALGO_ENUM = {
    "ECDSA": CryptoAlgorithm.ECDSA,
    "HYBRID": CryptoAlgorithm.HYBRID,
    "ML-DSA": CryptoAlgorithm.MLDSA,
}


class MigrationEngine:
    """Handles cryptographic migration of identities."""

    def migrate(self, db: Session, did: str, target_algorithm: str) -> dict:
        identity = db.query(Identity).filter(Identity.did == did).first()
        if not identity:
            raise ValueError("Identity not found")
        if identity.status == IdentityStatus.REVOKED:
            raise ValueError("Cannot migrate a revoked identity")

        old_algorithm = identity.algorithm.value
        if old_algorithm == target_algorithm:
            raise ValueError(f"Identity already uses {target_algorithm}")

        steps = []

        # Step 1: Generate new key pair
        provider = get_crypto_provider(target_algorithm)
        new_keypair = provider.generate_keypair()
        steps.append({"step": 1, "description": f"Generate {target_algorithm} key pair", "status": "completed"})

        # Step 2: Create migration transaction on blockchain
        old_key_ref = identity.public_key[:64] if identity.public_key else ""
        new_keyref = new_keypair.public_key.hex()[:64]
        tx_result = blockchain_service.record_migration(
            did, old_algorithm, target_algorithm, old_key_ref, new_keyref
        )
        steps.append({"step": 2, "description": "Record migration on blockchain", "status": "completed"})

        # Step 3: Associate new public key with DID
        new_identity_hash = compute_identity_hash(did, new_keypair.public_key.hex(), target_algorithm)
        identity.algorithm = _ALGO_ENUM.get(target_algorithm, CryptoAlgorithm.ECDSA)
        identity.public_key = new_keypair.public_key.hex()
        identity.identity_hash = new_identity_hash
        identity.security_level = new_keypair.security_level
        identity.last_migration_at = datetime.now(timezone.utc)
        steps.append({"step": 3, "description": "Associate new public key with DID", "status": "completed"})

        # Step 4: Store new key record
        new_key_record = IdentityKey(
            identity_id=identity.id,
            algorithm=_ALGO_ENUM.get(target_algorithm, CryptoAlgorithm.ECDSA),
            public_key=new_keypair.public_key.hex(),
            private_key_ref=new_keypair.private_key.hex(),
            is_active=True,
        )
        db.add(new_key_record)

        # Deactivate old keys
        old_keys = db.query(IdentityKey).filter(
            IdentityKey.identity_id == identity.id,
            IdentityKey.is_active == True,
        ).all()
        for k in old_keys:
            k.is_active = False
        steps.append({"step": 4, "description": "Update key records", "status": "completed"})

        # Step 5: Record migration event
        migration_event = MigrationEvent(
            identity_id=identity.id,
            old_algorithm=_ALGO_ENUM.get(old_algorithm, CryptoAlgorithm.ECDSA),
            new_algorithm=_ALGO_ENUM.get(target_algorithm, CryptoAlgorithm.ECDSA),
            old_public_key_ref=old_key_ref,
            new_public_key_ref=new_keyref,
            blockchain_tx_hash=tx_result.get("tx_hash") if tx_result else None,
            step_status="completed",
        )
        db.add(migration_event)
        steps.append({"step": 5, "description": "Record migration event", "status": "completed"})

        # Record blockchain transaction
        if tx_result:
            blockchain_tx = BlockchainTransaction(
                tx_hash=tx_result["tx_hash"],
                block_number=tx_result.get("block_number"),
                identity_did=did,
                event_type="migration_recorded",
                payload_hash=new_identity_hash,
                gas_used=tx_result.get("gas_used"),
                status=tx_result.get("status", "confirmed"),
            )
            db.add(blockchain_tx)

        db.commit()

        return {
            "did": did,
            "old_algorithm": old_algorithm,
            "new_algorithm": target_algorithm,
            "steps": steps,
            "completed": True,
            "blockchain_tx": tx_result,
        }

    def get_migration_history(self, db: Session, did: str) -> list[dict]:
        identity = db.query(Identity).filter(Identity.did == did).first()
        if not identity:
            return []

        events = (
            db.query(MigrationEvent)
            .filter(MigrationEvent.identity_id == identity.id)
            .order_by(MigrationEvent.created_at.asc())
            .all()
        )
        return [
            {
                "id": e.id,
                "old_algorithm": e.old_algorithm.value,
                "new_algorithm": e.new_algorithm.value,
                "blockchain_tx_hash": e.blockchain_tx_hash,
                "step_status": e.step_status,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ]


migration_engine = MigrationEngine()
