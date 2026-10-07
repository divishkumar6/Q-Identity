from app.crypto.base import ICryptoProvider, KeyPair, SignatureResult
from app.crypto.ecdsa_provider import ECDSAProvider
from app.crypto.mldsa_provider import MLDSAProvider


class HybridProvider(ICryptoProvider):
    """Hybrid cryptographic provider: ECDSA + ML-DSA.

    Both signatures are required for verification.
    Provides classical + post-quantum security.
    """

    def __init__(self):
        self._ecdsa = ECDSAProvider()
        self._mldsa = MLDSAProvider()

    def generate_keypair(self) -> KeyPair:
        ecdsa_kp = self._ecdsa.generate_keypair()
        mldsa_kp = self._mldsa.generate_keypair()

        combined_public = ecdsa_kp.public_key + b"||" + mldsa_kp.public_key
        combined_private = ecdsa_kp.private_key + b"||" + mldsa_kp.private_key

        return KeyPair(
            public_key=combined_public,
            private_key=combined_private,
            algorithm="HYBRID",
            security_level="ECDSA + ML-DSA",
            metadata={
                "ecdsa_metadata": ecdsa_kp.metadata,
                "mldsa_metadata": mldsa_kp.metadata,
                "security_level": 192,
                "nist_approved": True,
                "quantum_vulnerable": False,
            },
        )

    def sign(self, private_key_bytes: bytes, message: bytes) -> SignatureResult:
        parts = private_key_bytes.split(b"||", 1)
        ecdsa_priv = parts[0]
        mldsa_priv = parts[1]

        ecdsa_sig = self._ecdsa.sign(ecdsa_priv, message)
        mldsa_sig = self._mldsa.sign(mldsa_priv, message)

        combined_sig = ecdsa_sig.signature + b"||" + mldsa_sig.signature

        return SignatureResult(
            signature=combined_sig,
            algorithm="HYBRID",
            size=len(combined_sig),
        )

    def verify(self, public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
        parts = public_key_bytes.split(b"||", 1)
        ecdsa_pub = parts[0]
        mldsa_pub = parts[1]

        sig_parts = signature.split(b"||", 1)
        ecdsa_sig = sig_parts[0]
        mldsa_sig = sig_parts[1]

        ecdsa_valid = self._ecdsa.verify(ecdsa_pub, message, ecdsa_sig)
        mldsa_valid = self._mldsa.verify(mldsa_pub, message, mldsa_sig)

        return ecdsa_valid and mldsa_valid

    def get_algorithm_name(self) -> str:
        return "HYBRID"

    def get_signature_size(self) -> int:
        return self._ecdsa.get_signature_size() + self._mldsa.get_signature_size() + 2

    def get_public_key_size(self) -> int:
        return self._ecdsa.get_public_key_size() + self._mldsa.get_public_key_size() + 2

    def get_metadata(self) -> dict:
        return {
            "name": "Hybrid ECDSA + ML-DSA",
            "ecdsa": self._ecdsa.get_metadata(),
            "mldsa": self._mldsa.get_metadata(),
            "signature_size": f"~{self.get_signature_size()} bytes",
            "public_key_size": f"~{self.get_public_key_size()} bytes",
            "security_level": 192,
            "quantum_vulnerable": False,
            "underlying_problem": "ECDSA (ECDLP) + ML-DSA (MLWE/Module-SIS)",
            "quantum_threat": "Hybrid: classical ECDSA is quantum-vulnerable but ML-DSA layer provides post-quantum security",
            "standardization": "NIST FIPS 186-5 (ECDSA) + NIST FIPS 204 (ML-DSA)",
        }
