from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import engine, Base
from app.api import api_router
from app.blockchain.service import blockchain_service


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    blockchain_service.connect()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# Q-Identity: Quantum-Ready Blockchain-Based Decentralized Identity Management System

A production-ready decentralized identity system featuring:
- **Post-Quantum Cryptography**: Support for ECDSA, ML-DSA (FIPS 204), and Hybrid algorithms
- **Blockchain Anchoring**: Identity records immutably stored on blockchain
- **Challenge-Response Authentication**: Cryptographic proof of identity ownership
- **Quantum Readiness Analysis**: Real-time assessment of cryptographic algorithm vulnerability
- **Identity Migration**: Seamless upgrade from classical to post-quantum algorithms
- **Tamper Detection**: Integrity verification of identity records

## Quick Start

1. **Create User** → `POST /api/users`
2. **Create Identity** → `POST /api/identity/create` (generates keys, records on blockchain)
3. **Get Challenge** → `POST /api/identity/authenticate/challenge`
4. **Sign Challenge** → Use private key to sign (demo: `POST /api/demo/sign`)
5. **Verify** → `POST /api/identity/authenticate`
6. **View Blockchain Records** → `GET /api/blockchain/transactions`

## Algorithm Support

| Algorithm | Type | Quantum Resistant | Key Size | Sig Size | Security Level |
|-----------|------|-------------------|----------|----------|----------------|
| ECDSA | Classical | ❌ No | 32 bytes | 64 bytes | NIST Level 1 |
| ML-DSA | Post-Quantum | ✅ Yes | 1312 bytes | 2420 bytes | NIST Level 3 |
| HYBRID | Hybrid | ✅ Yes | 1344 bytes | 2484 bytes | Hybrid Level 3 |

## Demo Endpoints

Use `/api/demo/*` endpoints for testing key generation, signing, and verification without creating full identities.

## Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`
    """,
    lifespan=lifespan,
    contact={
        "name": "Skylark Drones",
        "url": "https://skylarkdrones.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "Users", "description": "User registration and management"},
        {"name": "Identity", "description": "Decentralized identity creation and management"},
        {"name": "Authentication", "description": "Challenge-response authentication flow"},
        {"name": "Migration", "description": "Post-quantum algorithm migration"},
        {"name": "Revocation", "description": "Identity revocation and status management"},
        {"name": "Integrity", "description": "Tamper detection and integrity verification"},
        {"name": "Quantum", "description": "Quantum readiness analysis and assessments"},
        {"name": "Blockchain", "description": "Blockchain transaction explorer"},
        {"name": "Benchmarks", "description": "Cryptographic performance benchmarks"},
        {"name": "Research", "description": "Research summary and analytics"},
        {"name": "Demo", "description": "Demo endpoints for testing crypto operations"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint - API information
    
    Returns basic API metadata including name, version, and status.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Root"])
def health():
    """
    Health check endpoint
    
    Returns simple health status for monitoring and load balancers.
    """
    return {"status": "healthy"}
