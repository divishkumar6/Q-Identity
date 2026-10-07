# Architecture

## System Overview

Q-Identity is a quantum-ready decentralized identity management system built with a layered architecture that separates concerns and enables cryptographic agility.

## High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│                  User Interface                  │
│              React + Tailwind CSS                │
└──────────────────────┬──────────────────────────┘
                       │ REST API
┌──────────────────────┴──────────────────────────┐
│                FastAPI Backend                    │
├──────────┬──────────┬──────────┬────────────────┤
│ Identity │   Auth   │   Cryp   │   Blockchain   │
│ Service  │ Service  │  Module  │    Service     │
├──────────┴──────────┴──────────┴────────────────┤
│              Crypto-Agility Layer                 │
│    ┌─────────┬──────────┬──────────────┐        │
│    │  ECDSA  │  Hybrid  │   ML-DSA     │        │
│    └─────────┴──────────┴──────────────┘        │
├─────────────────────────────────────────────────┤
│           Blockchain Layer (Hardhat)             │
│         IdentityRegistry Smart Contract          │
├─────────────────────────────────────────────────┤
│              SQLite / PostgreSQL                  │
└─────────────────────────────────────────────────┘
```

## Module Breakdown

### Backend (FastAPI)

| Module | Responsibility |
|--------|---------------|
| `app/api/` | REST endpoint definitions |
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic request/response schemas |
| `app/services/` | Business logic (identity, migration) |
| `app/crypto/` | Crypto-agility layer with provider abstraction |
| `app/blockchain/` | Ethereum/Hardhat blockchain integration |
| `app/quantum/` | Quantum readiness assessment engine |
| `app/benchmark/` | Performance measurement engine |
| `app/core/` | Configuration, database, security utilities |

### Crypto-Agility Layer

The core architectural innovation. All cryptographic operations go through an `ICryptoProvider` interface:

```
Application Code
       ↓
  ICryptoProvider (abstract)
       ↓
  ┌────┴────┐
  │ Factory │
  └────┬────┘
       ↓
  ECDSAProvider | HybridProvider | MLDSAProvider
```

This means the identity workflow never changes - only the cryptographic provider swaps underneath.

### Blockchain Layer

Solidity smart contract `IdentityRegistry` stores:
- DID (string identifier)
- Public key hash (bytes32)
- Identity hash (bytes32)
- Algorithm identifier
- Status (active/revoked/migrated)
- Version counter
- Timestamps

Private keys never touch the blockchain.

## Data Flow

### Identity Creation
1. User submits name, email, algorithm choice
2. Backend creates user record
3. Crypto provider generates key pair
4. DID is generated
5. Identity hash is computed
6. Public key hash + identity hash recorded on blockchain
7. Identity returned with blockchain transaction reference

### Authentication
1. Client requests challenge for a DID
2. Backend generates random 32-byte challenge, stores with expiry
3. Client signs challenge with private key (client-side)
4. Backend retrieves public key from identity record
5. Backend verifies signature using appropriate crypto provider
6. Backend checks blockchain identity status
7. Authentication result returned

### Migration
1. User selects identity and target algorithm
2. New key pair generated with target algorithm
3. Migration transaction recorded on blockchain
4. Identity record updated with new public key
5. Old keys deactivated, new key marked active
6. Migration event stored in history

## Database Schema

```
Users ──┬── Identities ──┬── IdentityKeys
        │                ├── AuthenticationChallenges
        │                ├── MigrationEvents
        │                └── RevocationEvents
        │
BlockchainTransactions (linked by DID)
BenchmarkRuns (independent)
QuantumAssessments (independent)
```

## Security Model

- Passwords: PBKDF2-HMAC-SHA256 with random salt (100,000 iterations)
- JWT: HS256 with configurable secret
- Challenges: Random hex, 5-minute expiry, single-use
- Private keys: Never stored in plaintext in database
- Blockchain: Only hashes and public key references stored on-chain
- API: Input validation via Pydantic schemas
