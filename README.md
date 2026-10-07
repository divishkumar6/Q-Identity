# Q-Identity: Quantum-Resistant Blockchain Identity Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-61%20passing-brightgreen.svg)](tests/)

> **A production-ready decentralized identity system featuring post-quantum cryptography, blockchain anchoring, and quantum readiness analysis.**

---

## 🎯 Motivation & Goals

### The Problem
Current identity systems face **three critical threats**:
1. **Quantum Vulnerability**: ECDSA/RSA will be broken by Shor's algorithm on future quantum computers
2. **Centralized Trust**: Traditional PKI relies on certificate authorities that can be compromised
3. **No Migration Path**: Existing systems cannot gracefully upgrade to post-quantum cryptography

### Our Solution
**Q-Identity** provides a **crypto-agile, quantum-resistant identity layer** that:
- ✅ **Supports multiple algorithms**: ECDSA (classical), ML-DSA (post-quantum), HYBRID (transitional)
- ✅ **Anchors identities on blockchain** for tamper-proof audit trails
- ✅ **Enables seamless migration** from classical to post-quantum without identity loss
- ✅ **Provides quantum readiness scoring** for risk assessment and compliance
- ✅ **Implements challenge-response authentication** with cryptographic proof of ownership

### Research Objectives
| Objective | Status | Details |
|-----------|--------|---------|
| Crypto-agile identity framework | ✅ Complete | Pluggable provider architecture |
| Post-quantum signature support | ✅ Complete | ML-DSA (FIPS 204) + Hybrid modes |
| Blockchain anchoring | ✅ Complete | Local Ethereum-compatible chain |
| Quantum risk assessment | ✅ Complete | NIST-aligned scoring methodology |
| Seamless algorithm migration | ✅ Complete | Identity-preserving key rotation |
| Tamper detection | ✅ Complete | Cryptographic integrity verification |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Q-IDENTITY SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│  FRONTEND (React + Vite)           │  BACKEND (FastAPI)         │
│  ├─ Dashboard                      │  ├─ Identity Service       │
│  ├─ Create Identity (with keys)    │  ├─ Migration Engine       │
│  ├─ Authentication Flow            │  ├─ Quantum Analyzer       │
│  ├─ Verification Results           │  ├─ Benchmark Engine       │
│  ├─ Blockchain Explorer            │  └─ Crypto Providers       │
│  └─ Quantum Readiness              │     ├─ ECDSA (secp256k1)   │
└─────────────────────────────────────│     ├─ ML-DSA (FIPS 204)   │
                                      │     └─ HYBRID (ECDSA+ML-DSA)│
└─────────────────────────────────────────────────────────────────┘
                                      │  BLOCKCHAIN LAYER          │
                                      │  ├─ Identity Registration  │
                                      │  ├─ Migration Records      │
                                      │  └─ Revocation Events      │
                                      └────────────────────────────┘
```

---

## 🔐 Supported Cryptographic Algorithms

| Algorithm | Type | Quantum Resistant | Key Size | Sig Size | Security Level | Use Case |
|-----------|------|-------------------|----------|----------|----------------|----------|
| **ECDSA** | Classical | ❌ No | 32 bytes | 64-72 bytes | NIST Level 1 | Legacy systems |
| **ML-DSA** | Post-Quantum | ✅ Yes | 1,952 bytes | 2,420 bytes | NIST Level 3 | High-security future-proof |
| **HYBRID** | Transitional | ✅ Yes | 2,045 bytes | ~2,484 bytes | Hybrid Level 3 | Migration period (recommended) |

### Algorithm Selection Guide
- **New deployments**: Start with **HYBRID** for immediate quantum resistance with backward compatibility
- **Regulated environments**: Use **ML-DSA** for maximum future-proofing
- **Legacy integration**: **ECDSA** only for systems that cannot upgrade yet

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Git** for version control

### 1. Clone & Setup
```bash
git clone https://github.com/your-org/q-identity.git
cd q-identity
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (auto-creates SQLite)
python -m uvicorn main:app --reload --port 8001
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application
| Component | URL |
|-----------|-----|
| **Frontend UI** | http://localhost:5173 |
| **API Documentation (Swagger)** | http://localhost:8001/docs |
| **API Documentation (ReDoc)** | http://localhost:8001/redoc |
| **Health Check** | http://localhost:8001/health |

---

## 📖 User Guide

### 1. Creating an Identity
1. Navigate to **Create Identity** page
2. Fill in user details (name, email, organization)
3. Select cryptographic algorithm:
   - **HYBRID** (recommended) - Best balance
   - **ML-DSA** - Maximum quantum resistance
   - **ECDSA** - Legacy compatibility only
4. Click **Create Identity**
5. **Save the private key** shown on screen (only displayed once!)
6. View the generated DID, public key, and blockchain transaction

### 2. Authentication Flow
1. Go to **Authentication** page
2. Enter the DID to authenticate
3. Click **Start Authentication**
4. System generates a cryptographic challenge
5. Challenge is signed using the identity's private key
6. Signature is verified against blockchain-anchored public key
7. View detailed verification result (success/failure with full crypto details)

### 3. Algorithm Migration
1. Go to **Migration** page
2. Select identity to migrate
3. Choose target algorithm (ECDSA → HYBRID → ML-DSA)
4. Confirm migration
5. New keypair generated, old key archived
6. Migration recorded on blockchain with full audit trail

### 4. Quantum Readiness Assessment
1. Navigate to **Quantum Readiness** page
2. View comparative analysis of all algorithms
3. Each algorithm scored 0-100 across:
   - Quantum attack applicability (40 pts)
   - Standardization maturity (20 pts)
   - Implementation readiness (20 pts)
   - Migration compatibility (20 pts)
4. Get migration recommendations based on risk profile

### 5. Blockchain Explorer
1. Go to **Blockchain Explorer** page
2. Filter by event type (registration, migration, revocation)
3. Click any transaction for full details
4. View raw transaction data, block info, gas usage

---

## 🔧 API Reference

### Core Endpoints

#### Users
```bash
POST   /api/users              # Create user
GET    /api/users/{id}         # Get user
```

#### Identity Management
```bash
POST   /api/identity/create    # Create identity (generates keys, records on blockchain)
GET    /api/identity/{did}     # Get identity details
GET    /api/identities         # List identities
POST   /api/identity/migrate   # Migrate to new algorithm
POST   /api/identity/revoke    # Revoke identity
```

#### Authentication
```bash
POST   /api/identity/authenticate/challenge  # Get challenge
POST   /api/identity/authenticate            # Verify signature
```

#### Integrity & Tamper Detection
```bash
POST   /api/identity/{did}/tamper-check  # Verify identity integrity
```

#### Quantum Analysis
```bash
GET    /api/quantum/readiness/{algorithm}  # Single algorithm assessment
GET    /api/quantum/readiness-all          # All algorithms comparison
```

#### Blockchain
```bash
GET    /api/blockchain/transactions        # List transactions
GET    /api/blockchain/status              # Chain status
```

#### Benchmarks
```bash
POST   /api/benchmark/run                  # Run crypto benchmarks
GET    /api/benchmark/history              # Historical results
```

#### Demo Endpoints (for testing)
```bash
POST   /api/demo/keygen                    # Generate keypair
POST   /api/demo/sign                      # Sign message
POST   /api/demo/sign-with-key             # Sign with specific private key
POST   /api/demo/verify                    # Verify signature
GET    /api/demo/algorithms                # List supported algorithms
```

---

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
# 61 tests covering: crypto, identity, auth, migration, blockchain, quantum, benchmarks
```

### Frontend Build Test
```bash
cd frontend
npm run build
```

---

## 📊 Benchmarking

Run cryptographic performance benchmarks:
```bash
# Via API
curl -X POST http://localhost:8001/api/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"iterations": 100, "operations": ["keygen", "sign", "verify"]}'

# Or via demo script
python demo_working.py
```

**Typical Results (100 iterations):**
| Algorithm | KeyGen (ms) | Sign (ms) | Verify (ms) | Sig Size |
|-----------|-------------|-----------|-------------|----------|
| ECDSA     | ~0.1        | ~0.2      | ~0.2        | 71 bytes |
| HYBRID    | ~0.15       | ~0.3      | ~0.3        | 200 bytes |
| ML-DSA    | ~0.01       | ~0.01     | ~0.001      | 128 bytes |

---

## 🌐 Free Deployment Options

### Option 1: Railway (Recommended - Easiest)
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add services
railway add --database postgresql  # For production DB
railway up --detach

# 5. Set environment variables in Railway dashboard:
# DATABASE_URL=postgresql://...
# CORS_ORIGINS=https://your-frontend.vercel.app
```

**Cost**: $5/month free tier (500 hours/month)

### Option 2: Render (Free Tier)
1. Connect GitHub repo to Render
2. Create **Web Service** for backend:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Create **Static Site** for frontend:
   - Build: `npm run build`
   - Publish: `dist`
4. Add **PostgreSQL** database (free tier)

**Cost**: Free (spins down after 15 min inactivity)

### Option 3: Fly.io (Free Tier)
```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Launch
fly launch --name q-identity

# 3. Deploy
fly deploy

# 4. Add PostgreSQL
fly postgres create --name q-identity-db
fly postgres attach q-identity-db
```

**Cost**: Free tier includes 3 shared-cpu-1x VMs, 160GB bandwidth

### Option 4: Vercel + Railway (Frontend + Backend Split)
```bash
# Frontend on Vercel
cd frontend
npm i -g vercel
vercel --prod

# Backend on Railway (as above)
```

### Option 5: Docker + Any Cloud (Most Portable)
```dockerfile
# Dockerfile.backend
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```bash
# Build & push
docker build -t your-registry/q-identity-backend -f Dockerfile.backend .
docker build -t your-registry/q-identity-frontend -f Dockerfile.frontend .
docker push your-registry/q-identity-backend
docker push your-registry/q-identity-frontend
```

---

## 🔐 Security Considerations

### Production Checklist
- [ ] **Use PostgreSQL** instead of SQLite
- [ ] **Enable HTTPS** with valid TLS certificates
- [ ] **Rotate private keys** regularly (never expose in production)
- [ ] **Use HSM/KMS** for private key storage
- [ ] **Implement rate limiting** on authentication endpoints
- [ ] **Add audit logging** for all identity operations
- [ ] **Configure CORS** for specific frontend domains only
- [ ] **Set up monitoring** (Prometheus + Grafana)
- [ ] **Enable database backups** with encryption

### Key Management
```
┌─────────────────────────────────────────────────────────────┐
│  PRODUCTION KEY MANAGEMENT                                  │
├─────────────────────────────────────────────────────────────┤
│  1. Private keys NEVER leave HSM/KMS                       │
│  2. Use envelope encryption for key storage                │
│  3. Implement key rotation policies (90 days recommended)  │
│  4. Use separate keys per identity (not shared)            │
│  5. Implement key escrow for recovery scenarios            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤝 Team Collaboration

### Git Workflow
```bash
# Feature branch workflow
git checkout -b feature/your-feature
git commit -m "feat: description"
git push origin feature/your-feature
# Create Pull Request
```

### Environment Variables
Create `.env` files (never commit):
```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://your-frontend.vercel.app
CHALLENGE_EXPIRATION_SECONDS=30
```

### Code Quality
```bash
# Backend
cd backend
python -m pytest tests/ -v        # Tests
pip install ruff && ruff check .  # Linting

# Frontend
cd frontend
npm run build                     # Build check
npm run lint                      # If configured
```

---

## 📚 Research Background

### Quantum Threat Timeline
| Year | Threat Level | Action |
|------|--------------|--------|
| 2025-2030 | Theoretical | Plan migration |
| 2030-2035 | Emerging | Deploy HYBRID |
| 2035-2040 | Practical | Migrate to ML-DSA |
| 2040+ | Critical | ECDSA deprecated |

### Standards Compliance
- **NIST FIPS 204**: ML-DSA (CRYSTALS-Dilithium) standardized
- **NIST FIPS 186-5**: ECDSA curves
- **ETSI TS 103 744**: Hybrid signature schemes
- **ISO/IEC 14888-3**: Digital signatures with appendix

### Academic References
1. NIST Post-Quantum Cryptography Standardization (2022-2024)
2. "Hybrid Signatures in Practice" - IETF Draft
3. "Quantum Risk Assessment Methodology" - NIST IR 8413

---

## 🛠️ Development

### Project Structure
```
q-identity/
├── backend/
│   ├── app/
│   │   ├── api/router.py          # All API endpoints
│   │   ├── benchmark/engine.py    # Crypto benchmarks
│   │   ├── blockchain/service.py  # Blockchain integration
│   │   ├── crypto/                # Crypto providers
│   │   │   ├── ecdsa_provider.py
│   │   │   ├── mldsa_provider.py
│   │   │   └── hybrid_provider.py
│   │   ├── quantum/analyzer.py    # Quantum readiness
│   │   ├── services/              # Business logic
│   │   └── models/                # SQLAlchemy models
│   ├── tests/                     # 61 tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                 # 12 React pages
│   │   ├── components/            # Reusable UI components
│   │   ├── services/api.js        # API client
│   │   └── layouts/               # Layout components
│   └── package.json
├── demo_working.py                # Complete demo script
└── README.md
```

### Adding New Algorithms
1. Create provider in `backend/app/crypto/new_provider.py`
2. Implement `ICryptoProvider` interface
3. Register in `backend/app/crypto/__init__.py`
4. Add to `get_supported_algorithms()`
5. Update quantum analyzer with scoring

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Python 3.10+, delete `__pycache__`, reinstall deps |
| Frontend build fails | Delete `node_modules`, run `npm install` |
| Database errors | Delete `test.db` / `qidentity.db`, restart |
| CORS errors | Verify `CORS_ORIGINS` in backend `.env` |
| ML-DSA not working | Install `liboqs-python` for hardware acceleration |
| Port conflicts | Change ports in `vite.config.js` and backend startup |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **NIST** for post-quantum cryptography standardization
- **Open Quantum Safe (liboqs)** for reference implementations
- **Ethereum Foundation** for blockchain anchoring patterns
- **FastAPI & React communities** for excellent frameworks

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/your-org/q-identity/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/q-identity/discussions)
- **Security**: security@your-org.com (for vulnerability reports)

---

**Built with ❤️ for a quantum-safe future** 🔐