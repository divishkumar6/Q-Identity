from web3 import Web3
from typing import Optional
import json
import os

from app.core.config import get_settings

settings = get_settings()

# Minimal ABI for the IdentityRegistry contract
IDENTITY_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "did", "type": "string"},
            {"name": "publicKeyHash", "type": "bytes32"},
            {"name": "identityHash", "type": "bytes32"},
            {"name": "algorithm", "type": "string"},
        ],
        "name": "registerIdentity",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "did", "type": "string"},
            {"name": "newPublicKeyHash", "type": "bytes32"},
            {"name": "newAlgorithm", "type": "string"},
        ],
        "name": "updatePublicKey",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "did", "type": "string"},
            {"name": "oldAlgorithm", "type": "string"},
            {"name": "newAlgorithm", "type": "string"},
            {"name": "oldKeyRef", "type": "bytes32"},
            {"name": "newKeyRef", "type": "bytes32"},
        ],
        "name": "recordMigration",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "did", "type": "string"}],
        "name": "revokeIdentity",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "did", "type": "string"}],
        "name": "getIdentity",
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "components": [
                    {"name": "did", "type": "string"},
                    {"name": "publicKeyHash", "type": "bytes32"},
                    {"name": "identityHash", "type": "bytes32"},
                    {"name": "algorithm", "type": "string"},
                    {"name": "status", "type": "uint8"},
                    {"name": "version", "type": "uint256"},
                    {"name": "createdAt", "type": "uint256"},
                    {"name": "updatedAt", "type": "uint256"},
                ],
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "did", "type": "string"}],
        "name": "verifyIdentityStatus",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "did", "type": "string"},
            {"indexed": False, "name": "algorithm", "type": "string"},
            {"indexed": False, "name": "publicKeyHash", "type": "bytes32"},
        ],
        "name": "IdentityRegistered",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "did", "type": "string"},
            {"indexed": False, "name": "oldAlgorithm", "type": "string"},
            {"indexed": False, "name": "newAlgorithm", "type": "string"},
        ],
        "name": "MigrationRecorded",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "did", "type": "string"},
        ],
        "name": "IdentityRevoked",
        "type": "event",
    },
]


class BlockchainService:
    """Blockchain integration service for identity operations."""

    def __init__(self):
        self._w3: Optional[Web3] = None
        self._contract = None
        self._connected = False

    def connect(self) -> bool:
        try:
            self._w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
            self._connected = self._w3.is_connected()
            if self._connected and settings.CONTRACT_ADDRESS:
                self._contract = self._w3.eth.contract(
                    address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
                    abi=IDENTITY_REGISTRY_ABI,
                )
            return self._connected
        except Exception:
            self._connected = False
            return False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def register_identity(
        self, did: str, public_key: bytes, identity_hash: str, algorithm: str
    ) -> Optional[dict]:
        if not self._connected or not self._contract:
            return self._mock_register(did, public_key, identity_hash, algorithm)

        try:
            pk_hash = Web3.keccak(public_key)
            ih = bytes.fromhex(identity_hash[:64])
            tx = self._contract.functions.registerIdentity(
                did, pk_hash, ih, algorithm
            ).transact({"from": self._w3.eth.accounts[0]})
            receipt = self._w3.eth.wait_for_transaction_receipt(tx)
            return {
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "confirmed",
            }
        except Exception as e:
            return {"tx_hash": "", "block_number": 0, "gas_used": 0, "status": f"failed: {str(e)}"}

    def update_public_key(
        self, did: str, new_public_key: bytes, new_algorithm: str
    ) -> Optional[dict]:
        if not self._connected or not self._contract:
            return self._mock_update(did, new_public_key, new_algorithm)

        try:
            pk_hash = Web3.keccak(new_public_key)
            tx = self._contract.functions.updatePublicKey(
                did, pk_hash, new_algorithm
            ).transact({"from": self._w3.eth.accounts[0]})
            receipt = self._w3.eth.wait_for_transaction_receipt(tx)
            return {
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "confirmed",
            }
        except Exception as e:
            return {"tx_hash": "", "block_number": 0, "gas_used": 0, "status": f"failed: {str(e)}"}

    def record_migration(
        self, did: str, old_algo: str, new_algo: str, old_key_ref: str, new_key_ref: str
    ) -> Optional[dict]:
        if not self._connected or not self._contract:
            return self._mock_migration(did, old_algo, new_algo)

        try:
            old_ref = bytes.fromhex(old_key_ref[:64]) if old_key_ref else b'\x00' * 32
            new_ref = bytes.fromhex(new_key_ref[:64]) if new_key_ref else b'\x00' * 32
            tx = self._contract.functions.recordMigration(
                did, old_algo, new_algo, old_ref, new_ref
            ).transact({"from": self._w3.eth.accounts[0]})
            receipt = self._w3.eth.wait_for_transaction_receipt(tx)
            return {
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "confirmed",
            }
        except Exception as e:
            return {"tx_hash": "", "block_number": 0, "gas_used": 0, "status": f"failed: {str(e)}"}

    def revoke_identity(self, did: str) -> Optional[dict]:
        if not self._connected or not self._contract:
            return self._mock_revoke(did)

        try:
            tx = self._contract.functions.revokeIdentity(did).transact(
                {"from": self._w3.eth.accounts[0]}
            )
            receipt = self._w3.eth.wait_for_transaction_receipt(tx)
            return {
                "tx_hash": receipt.transactionHash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "confirmed",
            }
        except Exception as e:
            return {"tx_hash": "", "block_number": 0, "gas_used": 0, "status": f"failed: {str(e)}"}

    def get_identity(self, did: str) -> Optional[dict]:
        if not self._connected or not self._contract:
            return None
        try:
            return self._contract.functions.getIdentity(did).call()
        except Exception:
            return None

    def get_block_number(self) -> int:
        if self._connected:
            return self._w3.eth.block_number
        return 0

    def _mock_register(self, did, public_key, identity_hash, algorithm):
        import hashlib
        import time
        mock_hash = hashlib.sha256(f"{did}:{identity_hash}:{time.time()}".encode()).hexdigest()
        return {
            "tx_hash": f"0x{mock_hash[:64]}",
            "block_number": 1,
            "gas_used": 21000,
            "status": "confirmed (local)",
        }

    def _mock_update(self, did, public_key, algorithm):
        import hashlib
        import time
        mock_hash = hashlib.sha256(f"update:{did}:{time.time()}".encode()).hexdigest()
        return {
            "tx_hash": f"0x{mock_hash[:64]}",
            "block_number": 2,
            "gas_used": 21000,
            "status": "confirmed (local)",
        }

    def _mock_migration(self, did, old_algo, new_algo):
        import hashlib
        import time
        mock_hash = hashlib.sha256(f"migrate:{did}:{old_algo}:{new_algo}:{time.time()}".encode()).hexdigest()
        return {
            "tx_hash": f"0x{mock_hash[:64]}",
            "block_number": 3,
            "gas_used": 21000,
            "status": "confirmed (local)",
        }

    def _mock_revoke(self, did):
        import hashlib
        import time
        mock_hash = hashlib.sha256(f"revoke:{did}:{time.time()}".encode()).hexdigest()
        return {
            "tx_hash": f"0x{mock_hash[:64]}",
            "block_number": 4,
            "gas_used": 21000,
            "status": "confirmed (local)",
        }


blockchain_service = BlockchainService()
