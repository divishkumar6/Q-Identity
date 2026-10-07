from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class KeyPair:
    public_key: bytes
    private_key: bytes
    algorithm: str
    security_level: str | None = None
    metadata: dict | None = None


@dataclass
class SignatureResult:
    signature: bytes
    algorithm: str
    size: int


class ICryptoProvider(ABC):
    """Abstract interface for cryptographic operations."""

    @abstractmethod
    def generate_keypair(self) -> KeyPair:
        pass

    @abstractmethod
    def sign(self, private_key: bytes, message: bytes) -> SignatureResult:
        pass

    @abstractmethod
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        pass

    @abstractmethod
    def get_algorithm_name(self) -> str:
        pass

    @abstractmethod
    def get_signature_size(self) -> int:
        pass

    @abstractmethod
    def get_public_key_size(self) -> int:
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        pass
