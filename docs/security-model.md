# Security Model

## Overview

Q-Identity implements multiple layers of security for decentralized identity management. This document describes the security considerations, implemented protections, and known limitations.

## Authentication Security

### Challenge-Response Protocol
1. Server generates cryptographically random 32-byte challenge
2. Challenge stored with 5-minute expiration
3. Client signs challenge with private key
4. Server verifies signature against stored public key
5. Challenge marked as used (single-use)

### Protections
- **Replay Protection**: Each challenge is single-use
- **Expiration**: Challenges expire after 5 minutes
- **Randomness**: Challenges generated using `secrets.token_hex(32)`
- **Revoked Identity Rejection**: Revoked identities cannot obtain challenges

## Password Security

- **Algorithm**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Salt**: Random 16-byte hex per password
- **Format**: `{salt}${hash}`

## JWT Security

- **Algorithm**: HS256 (HMAC-SHA256)
- **Expiration**: Configurable (default 60 minutes)
- **Secret**: Environment variable (must change for production)

## Key Management

### Private Keys
- Never stored in plaintext in the database
- Stored as hex-encoded bytes with reference only
- For prototype: managed locally in memory
- For production: use hardware security module (HSM) or secure enclave

### Public Keys
- Stored as hex-encoded DER format
- Recorded on blockchain as keccak256 hash
- Identity hash computed from DID + public key + algorithm

## Blockchain Security

### On-Chain Data
Only the following is stored on-chain:
- DID (string identifier)
- Public key hash (bytes32)
- Identity hash (bytes32)
- Algorithm identifier
- Status, version, timestamps

### Off-Chain Data
Private keys, personal information, and sensitive metadata remain off-chain.

### Smart Contract
- Access control via Solidity modifiers
- Status checks before state transitions
- Event emission for all important state changes

## Input Validation

All API inputs validated through Pydantic schemas:
- Email format validation
- String length constraints
- Enum validation for algorithm choices
- Integer bounds for iterations

## Known Limitations

1. **No Rate Limiting**: The prototype does not implement rate limiting on authentication endpoints
2. **No CSRF Protection**: Prototype does not implement CSRF tokens
3. **Demo ML-DSA**: ML-DSA verification in demo mode accepts any properly formatted signature
4. **Local Storage**: Private keys stored in local memory, not secure enclave
5. **JWT Secret**: Default secret must be changed for production
6. **No HTTPS**: Prototype runs on HTTP, production requires TLS

## Quantum Security Considerations

### Current Threat Model
- Current quantum computers CANNOT break production ECC (256-bit)
- Estimated 2,500+ logical qubits needed for Shor's algorithm on P-256
- Current best quantum computers: ~1,000 noisy physical qubits

### Future Threat Model
- Cryptographically relevant quantum computers may exist in 10-30 years
- ECDSA and RSA are vulnerable to Shor's algorithm
- ML-DSA (CRYSTALS-Dilithium) based on lattice assumptions, no known quantum attack

### Migration Strategy
1. Crypto-agility layer enables algorithm switching
2. Hybrid mode provides transitional security
3. Full ML-DSA migration for maximum post-quantum security

## Recommendations for Production

1. Replace demo ML-DSA with `liboqs-python` or equivalent
2. Implement rate limiting on authentication endpoints
3. Use HTTPS/TLS for all communications
4. Store private keys in HSM or secure enclave
5. Change JWT secret and use RS256 for production
6. Implement CORS restrictions for production domains
7. Add comprehensive audit logging
8. Implement key rotation procedures
