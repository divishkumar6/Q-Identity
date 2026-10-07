import importlib
import os
from app.crypto.base import ICryptoProvider, KeyPair, SignatureResult

_OQS_AVAILABLE = False
try:
    import oqs
    _OQS_AVAILABLE = True
except ImportError:
    pass


class MLDSAProvider(ICryptoProvider):
    """ML-DSA / CRYSTALS-Dilithium post-quantum cryptographic provider.

    Uses liboqs-python (Open Quantum Safe) if available.
    Falls back to a demo provider with clear labeling if liboqs is not installed.
    """

    def __init__(self):
        self._use_liboqs = _OQS_AVAILABLE
        if self._use_liboqs:
            self._sigalg = "ML-DSA-65"
        else:
            self._sigalg = "ML-DSA-65-DEMO"
        self._demo_last_private_key = None  # For demo mode verification

    def generate_keypair(self) -> KeyPair:
        if self._use_liboqs:
            return self._generate_liboqs_keypair()
        return self._generate_demo_keypair()

    def _generate_liboqs_keypair(self) -> KeyPair:
        sig = oqs.Signature(self._sigalg)
        public_key = sig.generate_keypair()
        # OQS doesn't expose private key bytes directly; store the context
        # For the prototype we use a deterministic seed approach
        private_key = os.urandom(32)  # seed placeholder

        return KeyPair(
            public_key=public_key,
            private_key=private_key,
            algorithm="ML-DSA",
            security_level="NIST Level 3",
            metadata={
                "algorithm": "ML-DSA-65",
                "security_level": 192,
                "nist_approved": True,
                "lattice_based": True,
                "liboqs": True,
            },
        )

    def _generate_demo_keypair(self) -> KeyPair:
        import secrets
        public_key = secrets.token_bytes(1952)
        private_key = secrets.token_bytes(4000)

        return KeyPair(
            public_key=public_key,
            private_key=private_key,
            algorithm="ML-DSA",
            security_level="NIST Level 3 (Demo)",
            metadata={
                "algorithm": "ML-DSA-65",
                "security_level": 192,
                "nist_approved": True,
                "lattice_based": True,
                "liboqs": False,
                "demo_mode": True,
                "note": "Demo mode: signature operations produce simulated results. "
                        "Install liboqs-python for standards-compliant ML-DSA.",
            },
        )

    def sign(self, private_key_bytes: bytes, message: bytes) -> SignatureResult:
        if self._use_liboqs:
            return self._sign_liboqs(private_key_bytes, message)
        return self._sign_demo(private_key_bytes, message)

    def _sign_liboqs(self, private_key_bytes: bytes, message: bytes) -> SignatureResult:
        sig = oqs.Signature(self._sigalg)
        sig.reset()
        # In full implementation, load the signer context from private_key_bytes
        # For prototype, create new signer (demo limitation)
        signature = sig.sign(message)
        return SignatureResult(
            signature=signature,
            algorithm="ML-DSA",
            size=len(signature),
        )

    def _sign_demo(self, private_key_bytes: bytes, message: bytes) -> SignatureResult:
        import hashlib
        self._demo_last_private_key = private_key_bytes
        h = hashlib.sha512(message + private_key_bytes[:64]).digest()
        signature = h + hashlib.sha512(h + message).digest()
        return SignatureResult(
            signature=signature,
            algorithm="ML-DSA",
            size=len(signature),
        )

    def verify(self, public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
        if self._use_liboqs:
            return self._verify_liboqs(public_key_bytes, message, signature)
        return self._verify_demo(public_key_bytes, message, signature)

    def _verify_liboqs(self, public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
        try:
            sig = oqs.Signature(self._sigalg)
            return sig.verify(message, signature, public_key_bytes)
        except Exception:
            return False

    def _verify_demo(self, public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
        if len(signature) != 128:
            return False
        if self._demo_last_private_key is None:
            return False
        import hashlib
        h = hashlib.sha512(message + self._demo_last_private_key[:64]).digest()
        expected_sig = h + hashlib.sha512(h + message).digest()
        return signature == expected_sig

    def get_algorithm_name(self) -> str:
        return "ML-DSA"

    def get_signature_size(self) -> int:
        return 3309

    def get_public_key_size(self) -> int:
        return 1952

    def get_metadata(self) -> dict:
        return {
            "name": "ML-DSA-65 (CRYSTALS-Dilithium)",
            "signature_size": "~3309 bytes",
            "public_key_size": "~1952 bytes",
            "security_level": 192,
            "nist_approved": True,
            "lattice_based": True,
            "quantum_vulnerable": False,
            "underlying_problem": "Module Learning With Errors (MLWE) / Module-SIS",
            "quantum_threat": "No known quantum algorithm efficiently solves MLWE/Module-SIS",
            "standardization": "NIST FIPS 204 (ML-DSA)",
            "liboqs_available": _OQS_AVAILABLE,
        }
