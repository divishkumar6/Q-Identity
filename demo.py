#!/usr/bin/env python3
"""
Q-Identity Working Demo Script

This script demonstrates the complete flow:
1. User registration
2. Identity creation with key generation
3. Challenge generation
4. Digital signature creation
5. Signature verification
6. Blockchain record
7. Final authentication result
"""

import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_json(data: Dict, title: str = ""):
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2))

def demo_keygen():
    """Demo: Key Generation"""
    print_section("1. KEY GENERATION")
    
    algorithms = ["ECDSA", "HYBRID", "ML-DSA"]
    
    for algo in algorithms:
        print(f"\n--- Generating {algo} Keypair ---")
        response = requests.post(f"{API_BASE}/demo/keygen", json={"algorithm": algo})
        result = response.json()
        
        print(f"Algorithm: {result['algorithm']}")
        print(f"Public Key: {result['public_key']}")
        print(f"Private Key: {result['private_key'][:32]}... (truncated)")
        print(f"Key Size: {result['key_size_bytes']} bytes")
        print(f"Security Level: {result['security_level']}")
        print(f"Details: {result['algorithm_details']}")

def demo_sign_verify():
    """Demo: Digital Signing and Verification"""
    print_section("2. DIGITAL SIGNATURE & VERIFICATION")
    
    message = "demo-challenge-12345"
    algorithms = ["ECDSA", "HYBRID", "ML-DSA"]
    
    for algo in algorithms:
        print(f"\n--- Signing with {algo} ---")
        
        # Sign
        sign_resp = requests.post(f"{API_BASE}/demo/sign", json={
            "algorithm": algo,
            "message": message
        })
        sign_result = sign_resp.json()
        
        print(f"Message: {sign_result['message']}")
        print(f"Public Key: {sign_result['public_key']}")
        print(f"Signature: {sign_result['signature']}")
        print(f"Signature Size: {sign_result['signature_size_bytes']} bytes")
        
        # Verify
        print(f"\n--- Verifying {algo} Signature ---")
        verify_resp = requests.post(f"{API_BASE}/demo/verify", json={
            "algorithm": algo,
            "message": message,
            "signature": sign_result['signature'],
            "public_key": sign_result['public_key']
        })
        verify_result = verify_resp.json()
        
        print(f"Valid: {verify_result['valid']}")
        print(f"Details: {verify_result['details']}")
        
        # Test invalid signature
        print(f"\n--- Testing Invalid Signature ---")
        invalid_sig = sign_result['signature'][:-1] + ('0' if sign_result['signature'][-1] != '0' else '1')
        verify_resp2 = requests.post(f"{API_BASE}/demo/verify", json={
            "algorithm": algo,
            "message": message,
            "signature": invalid_sig,
            "public_key": sign_result['public_key']
        })
        verify_result2 = verify_resp2.json()
        print(f"Valid: {verify_result2['valid']}")
        print(f"Details: {verify_result2['details']}")

def demo_full_flow():
    """Demo: Complete Identity Flow"""
    print_section("3. COMPLETE IDENTITY FLOW")
    
    # Step 1: Create User
    print("--- Step 1: Create User ---")
    user_data = {
        "name": "Demo User",
        "email": f"demo{int(time.time())}@example.com",
        "organization": "Skylark Drones",
        "password": "demo-password-123"
    }
    resp = requests.post(f"{API_BASE}/users", json=user_data)
    user = resp.json()
    print(f"User ID: {user['id']}")
    print(f"Name: {user['name']}")
    print(f"Email: {user['email']}")
    
    # Step 2: Create Identity (with key generation)
    print("\n--- Step 2: Create Identity (Key Generation) ---")
    identity_resp = requests.post(f"{API_BASE}/identity/create", json={
        "user_id": user['id'],
        "algorithm": "HYBRID"
    })
    identity = identity_resp.json()
    
    print(f"DID: {identity['did']}")
    print(f"Algorithm: {identity['algorithm']}")
    print(f"Public Key: {identity['public_key']}")
    print(f"Private Key (demo): {identity.get('private_key_ref', 'N/A')[:32]}... (truncated)")
    print(f"Identity Hash: {identity['identity_hash']}")
    print(f"Security Level: {identity['security_level']}")
    print(f"Blockchain TX: {identity['blockchain_tx'].get('tx_hash')}")
    print(f"Block Number: {identity['blockchain_tx'].get('block_number')}")
    
    did = identity['did']
    
    # Step 3: Get Challenge
    print("\n--- Step 3: Get Authentication Challenge ---")
    challenge_resp = requests.post(f"{API_BASE}/identity/authenticate/challenge?did={did}")
    challenge = challenge_resp.json()
    print(f"Challenge: {challenge['challenge']}")
    print(f"Expires: {challenge['expires_at']}")
    
    # Step 4: Sign Challenge
    print("\n--- Step 4: Sign Challenge (Digital Signature) ---")
    sign_resp = requests.post(f"{API_BASE}/demo/sign", json={
        "algorithm": "HYBRID",
        "message": challenge['challenge']
    })
    sign_result = sign_resp.json()
    print(f"Signature: {sign_result['signature']}")
    print(f"Message Signed: {sign_result['message']}")
    
    # Step 5: Verify Authentication
    print("\n--- Step 5: Verify Authentication ---")
    auth_resp = requests.post(f"{API_BASE}/identity/authenticate", json={
        "did": did,
        "signature": sign_result['signature']
    })
    auth_result = auth_resp.json()
    
    print(f"Verified: {auth_result['verified']}")
    print(f"Message: {auth_result['message']}")
    print(f"Identity Status: {auth_result['identity_status']}")
    print(f"Algorithm: {auth_result['algorithm']}")
    print(f"Blockchain Verified: {auth_result['blockchain_verified']}")
    
    # Step 6: Check Blockchain Records
    print("\n--- Step 6: Blockchain Records ---")
    bc_resp = requests.get(f"{API_BASE}/blockchain/transactions?did={did}")
    bc_data = bc_resp.json()
    for tx in bc_data:
        print(f"  Block: {tx.get('block_number')} | Event: {tx.get('event_type')} | Tx: {tx.get('tx_hash')[:24]}... | Status: {tx.get('status')}")
    
    # Step 7: Tamper Check
    print("\n--- Step 7: Integrity/Tamper Check ---")
    tamper_resp = requests.post(f"{API_BASE}/identity/{did}/tamper-check")
    tamper = tamper_resp.json()
    print(f"Integrity Valid: {tamper['integrity_valid']}")
    print(f"Message: {tamper['message']}")
    print(f"Original Hash: {tamper['original_hash'][:32]}...")
    print(f"Current Hash: {tamper['current_hash'][:32]}...")
    
    return {
        "user": user,
        "identity": identity,
        "challenge": challenge,
        "signature": sign_result,
        "auth_result": auth_result,
        "blockchain": bc_data,
        "tamper_check": tamper
    }

def demo_benchmarks():
    """Demo: Cryptographic Benchmarks"""
    print_section("4. CRYPTOGRAPHIC BENCHMARKS")
    
    print("Running benchmarks (100 iterations each)...")
    resp = requests.post(f"{API_BASE}/benchmark/run", json={
        "iterations": 100,
        "operations": ["keygen", "sign", "verify"]
    })
    results = resp.json()
    
    print("\n--- Benchmark Results ---")
    print(f"{'Algorithm':<10} {'Operation':<12} {'Avg (ms)':<10} {'Min (ms)':<10} {'Max (ms)':<10} {'Sig Size':<10} {'Key Size':<10}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['algorithm']:<10} {r['operation']:<12} {r['avg_time_ms']:<10.4f} {r['min_time_ms']:<10.4f} {r['max_time_ms']:<10.4f} {str(r.get('avg_signature_size', 'N/A')):<10} {str(r.get('avg_key_size', 'N/A')):<10}")
    
    # Get history
    hist_resp = requests.get(f"{API_BASE}/benchmark/history?limit=10")
    history = hist_resp.json()
    print(f"\nHistory records: {len(history)}")

def demo_quantum_readiness():
    """Demo: Quantum Readiness Analysis"""
    print_section("5. QUANTUM READINESS ANALYSIS")
    
    resp = requests.get(f"{API_BASE}/quantum/readiness-all")
    assessments = resp.json()
    
    for algo, assessment in assessments.items():
        print(f"\n--- {algo} ---")
        print(f"  Overall Score: {assessment['overall_score']}/100")
        print(f"  Risk Level: {assessment['risk_level']}")
        print(f"  Years to Quantum Threat: {assessment['years_to_threat']}")
        print(f"  Recommendation: {assessment['recommendation']}")
        print(f"  Breakdown:")
        for cat, score in assessment['breakdown'].items():
            print(f"    {cat}: {score}/100")

def main():
    print("\n" + "🔐" * 30)
    print("  Q-IDENTITY QUANTUM-RESISTANT IDENTITY SYSTEM")
    print("  Complete Working Demo")
    print("  " + "🔐" * 30)
    
    try:
        # Check if backend is running
        health = requests.get(f"{BASE_URL}/health", timeout=2)
        if health.status_code != 200:
            print("\n❌ Backend not running. Start it with: cd backend && python -m uvicorn app.main:app --reload")
            sys.exit(1)
    except Exception:
        print("\n❌ Backend not accessible at http://localhost:8000")
        print("   Start the backend: cd backend && python -m uvicorn app.main:app --reload")
        sys.exit(1)
    
    print("\n✅ Backend is running")
    
    # Run all demos
    demo_keygen()
    demo_sign_verify()
    demo_full_flow()
    demo_benchmarks()
    demo_quantum_readiness()
    
    print_section("✅ DEMO COMPLETE")
    print("All demonstrations completed successfully!")
    print("\nAccess the web UI at: http://localhost:5173")
    print("API Documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()