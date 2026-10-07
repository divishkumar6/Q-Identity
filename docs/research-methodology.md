# Research Methodology

## Problem Statement

Classical public-key cryptography (ECDSA) used by blockchain-based identity systems may be threatened by future cryptographically relevant quantum computers running Shor's algorithm. This project studies the practical migration of blockchain-based decentralized identity systems toward post-quantum cryptography.

**Important:** Current quantum computers cannot practically break production-strength blockchain cryptography. This project addresses the future threat model.

## Approach

1. **Crypto-Agility Layer**: Abstract cryptographic operations behind a common interface (`ICryptoProvider`), allowing seamless switching between ECDSA, Hybrid (ECDSA+ML-DSA), and ML-DSA without changing the identity workflow.

2. **Quantum Readiness Assessment**: Transparent scoring system based on known cryptographic assumptions, quantum attack applicability, and NIST standardization status.

3. **Performance Benchmarking**: Real measurements of cryptographic operations with statistical aggregation across multiple iterations.

## Algorithms Under Study

| Algorithm | Type | Standard | Security Basis | QR Score |
|-----------|------|----------|---------------|----------|
| ECDSA | Classical | NIST FIPS 186-5 | ECDLP | 32/100 |
| Hybrid | Classical+PQC | Combined | ECDLP + MLWE/Module-SIS | 72/100 |
| ML-DSA | Post-Quantum | NIST FIPS 204 | MLWE / Module-SIS | 92/100 |

## Measurements

### Cryptographic Performance
- Key generation time (ms)
- Signing time (ms)
- Verification time (ms)
- Public key size (bytes)
- Signature size (bytes)

### Blockchain Impact
- Transaction payload size
- Storage growth per identity
- Migration transaction cost
- Verification latency

### Statistical Rigor
- Each operation repeated 10-1000 iterations
- Minimum, maximum, average, median, standard deviation reported
- No single-execution results used

## Experiment Design

### Experiment A: Classical Identity
- ECDSA key generation
- ECDSA signing/verification
- Blockchain registration
- Authentication latency

### Experiment B: Hybrid Identity
- ECDSA + ML-DSA dual key generation
- Dual signing (both signatures required)
- Blockchain registration with larger payload
- Authentication with both verifications

### Experiment C: Post-Quantum Identity
- ML-DSA key generation
- ML-DSA signing/verification
- Blockchain registration with largest payload
- Authentication latency

### Experiment D: Migration
- ECDSA → Hybrid migration time and overhead
- Hybrid → ML-DSA migration time and overhead
- Identity preservation across migrations

## Quantum Readiness Scoring

### Factors (100-point scale)
1. **Quantum Attack Applicability** (40 points): Does a known quantum algorithm break this?
2. **Standardization Status** (20 points): Is this NIST-standardized?
3. **Implementation Readiness** (20 points): Is this production-ready?
4. **Migration Compatibility** (20 points): Can existing systems adopt this?

### Scores
- ECDSA: 32/100 (quantum-vulnerable)
- Hybrid: 72/100 (transitional protection)
- ML-DSA: 92/100 (post-quantum ready)

**Disclaimer:** This score is a project-defined assessment metric and is not an official security rating.

## Limitations

1. ML-DSA operates in demo mode unless `liboqs-python` is installed
2. Blockchain transactions are simulated when no local node is running
3. Benchmark results reflect prototype implementation, not optimized production code
4. Current quantum hardware is NOT capable of breaking production ECC
5. Security assessments are based on current cryptographic assumptions and may change with future research

## Expected Findings

1. ML-DSA signatures are significantly larger than ECDSA (~3309 bytes vs ~72 bytes)
2. ML-DSA key generation is slower than ECDSA
3. Verification times may be comparable or faster for ML-DSA
4. Blockchain transaction size increases significantly with ML-DSA
5. Migration cost is measurable but manageable
6. Crypto-agility layer successfully decouples identity workflow from cryptographic implementation
