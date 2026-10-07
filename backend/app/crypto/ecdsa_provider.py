import hashlib
import secrets
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

from app.crypto.base import ICryptoProvider, KeyPair, SignatureResult


class ECDSAProvider(ICryptoProvider):
    """ECDSA cryptographic provider using secp256r1 (P-256)."""

    def __init__(self):
        self._curve = ec.SECP256R1()

    def generate_keypair(self) -> KeyPair:
        private_key = ec.generate_private_key(self._curve, default_backend())
        public_key = private_key.public_key()

        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return KeyPair(
            public_key=public_bytes,
            private_key=private_bytes,
            algorithm="ECDSA",
            security_level="NIST P-256",
            metadata={
                "curve": "secp256r1",
                "security_level": 128,
                "nist_approved": True,
            },
        )

    def sign(self, private_key_bytes: bytes, message: bytes) -> SignatureResult:
        private_key = serialization.load_der_private_key(
            private_key_bytes, password=None, backend=default_backend()
        )
        signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
        return SignatureResult(
            signature=signature,
            algorithm="ECDSA",
            size=len(signature),
        )

    def verify(self, public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
        try:
            public_key = serialization.load_der_public_key(
                public_key_bytes, backend=default_backend()
            )
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False

    def get_algorithm_name(self) -> str:
        return "ECDSA"

    def get_signature_size(self) -> int:
        return 72

    def get_public_key_size(self) -> int:
        return 91

    def get_metadata(self) -> dict:
        return {
            "name": "ECDSA",
            "curve": "secp256r1",
            "signature_size": "~72 bytes",
            "public_key_size": "~91 bytes",
            "security_level": 128,
            "nist_approved": True,
            "quantum_vulnerable": True,
            "underlying_problem": "Elliptic Curve Discrete Logarithm Problem",
            "quantum_threat": "Shor's algorithm can solve ECDLP in polynomial time on a sufficiently large quantum computer",
        }
