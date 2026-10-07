# API Documentation

Base URL: `http://localhost:8001/api`

## Identity Management

### Create User
```
POST /api/users
Body: { "name": "string", "email": "string", "password": "string", "organization": "string?" }
Response: { "id": 1, "name": "...", "email": "...", "created_at": "..." }
```

### Create Identity
```
POST /api/identity/create
Body: { "user_id": 1, "algorithm": "ECDSA" | "HYBRID" | "ML-DSA" }
Response: { "id": 1, "did": "did:qidentity:...", "algorithm": "...", "public_key": "...", "blockchain_tx": {...} }
```

### Get Identity
```
GET /api/identity/{did}
Response: { "id": 1, "did": "...", "status": "active", "algorithm": "...", "identity_hash": "..." }
```

### List Identities
```
GET /api/identities?user_id=1&limit=50
Response: [{ "did": "...", "status": "...", "algorithm": "..." }]
```

## Authentication

### Get Challenge
```
POST /api/identity/authenticate/challenge?did=did:qidentity:...
Response: { "challenge": "hex_string", "expires_at": "ISO_datetime" }
```

### Authenticate
```
POST /api/identity/authenticate
Body: { "did": "did:qidentity:...", "signature": "hex_string" }
Response: { "verified": true/false, "message": "...", "algorithm": "..." }
```

## Migration

### Migrate Identity
```
POST /api/identity/migrate
Body: { "did": "did:qidentity:...", "target_algorithm": "ECDSA" | "HYBRID" | "ML-DSA" }
Response: { "did": "...", "old_algorithm": "...", "new_algorithm": "...", "steps": [...], "completed": true }
```

### Migration History
```
GET /api/identity/{did}/migration-history
Response: [{ "old_algorithm": "...", "new_algorithm": "...", "created_at": "..." }]
```

## Revocation

### Revoke Identity
```
POST /api/identity/revoke
Body: { "did": "did:qidentity:...", "reason": "string?" }
Response: { "did": "...", "status": "revoked", "blockchain_tx": {...} }
```

## Tampering Detection

### Integrity Check
```
POST /api/identity/{did}/tamper-check?modified_name=string
Response: { "original_hash": "...", "current_hash": "...", "integrity_valid": true/false }
```

## Quantum Readiness

### Get Assessment
```
GET /api/quantum/readiness/{algorithm}
Response: { "assessment": { "algorithm": "...", "quantum_readiness_score": 32, "is_vulnerable": true, ... } }
```

### All Assessments
```
GET /api/quantum/readiness-all
Response: { "ECDSA": {...}, "HYBRID": {...}, "ML-DSA": {...} }
```

## Benchmarks

### Run Benchmark
```
POST /api/benchmark/run
Body: { "algorithm": "ECDSA"?, "iterations": 100, "operations": ["keygen", "sign", "verify"] }
Response: [{ "algorithm": "...", "operation": "...", "avg_time_ms": 0.14, ... }]
```

### Benchmark History
```
GET /api/benchmark/history?algorithm=ECDSA&limit=50
Response: [{ "algorithm": "...", "operation": "...", "avg_time_ms": ... }]
```

## Blockchain

### Transactions
```
GET /api/blockchain/transactions?did=did:qidentity:...&limit=50
Response: [{ "tx_hash": "...", "event_type": "...", "identity_did": "..." }]
```

### Status
```
GET /api/blockchain/status
Response: { "connected": false, "mode": "local", "block_number": 0 }
```

## Research

### Summary
```
GET /api/research/summary
Response: { "total_identities": 10, "pqc_identities": 5, "total_transactions": 20, ... }
```

## Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```
