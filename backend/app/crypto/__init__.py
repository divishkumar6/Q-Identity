from app.crypto.base import ICryptoProvider
from app.crypto.ecdsa_provider import ECDSAProvider
from app.crypto.mldsa_provider import MLDSAProvider
from app.crypto.hybrid_provider import HybridProvider

_PROVIDERS: dict[str, type[ICryptoProvider]] = {
    "ECDSA": ECDSAProvider,
    "HYBRID": HybridProvider,
    "ML-DSA": MLDSAProvider,
}


def get_crypto_provider(algorithm: str) -> ICryptoProvider:
    """Factory function to get the appropriate crypto provider."""
    provider_class = _PROVIDERS.get(algorithm.upper())
    if not provider_class:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Supported: {list(_PROVIDERS.keys())}")
    return provider_class()


def get_supported_algorithms() -> list[str]:
    return list(_PROVIDERS.keys())


__all__ = [
    "get_crypto_provider",
    "get_supported_algorithms",
    "ECDSAProvider",
    "MLDSAProvider",
    "HybridProvider",
    "ICryptoProvider",
]
