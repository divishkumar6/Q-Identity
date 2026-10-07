import subprocess
import time
import sys
import requests
import threading

def run_demo():
    # Start backend server
    print("Starting backend server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd=r"C:\Users\divis\OneDrive\Desktop\skylarkdrones\q-identity\backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Read server output in background
    def read_output():
        for line in proc.stdout:
            if "Uvicorn running on" in line or "Application startup complete" in line:
                print(f"  Server: {line.strip()}")
    
    reader_thread = threading.Thread(target=read_output, daemon=True)
    reader_thread.start()
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test health with retries
        for attempt in range(10):
            try:
                resp = requests.get("http://localhost:8001/health", timeout=3)
                if resp.status_code == 200:
                    print(f"Health check: {resp.json()}")
                    break
            except Exception as e:
                if attempt == 9:
                    raise
                time.sleep(0.5)
        
        # Run the demo
        print("\n" + "[LOCK]" * 30)
        print("  Q-IDENTITY QUANTUM-RESISTANT IDENTITY SYSTEM")
        print("  Complete Working Demo")
        print("  " + "[LOCK]" * 30)
        
        BASE_URL = "http://localhost:8001"
        API_BASE = f"{BASE_URL}/api"
        
        # Demo 1: Key Generation
        print("\n" + "="*60)
        print("  1. KEY GENERATION")
        print("="*60)
        
        for algo in ["ECDSA", "HYBRID", "ML-DSA"]:
            print(f"\n--- Generating {algo} Keypair ---")
            response = requests.post(f"{API_BASE}/demo/keygen", json={"algorithm": algo})
            result = response.json()
            print(f"Algorithm: {result['algorithm']}")
            print(f"Public Key: {result['public_key']}")
            print(f"Private Key: {result['private_key'][:32]}... (truncated)")
            print(f"Key Size: {result['key_size_bytes']} bytes")
            print(f"Security Level: {result['security_level']}")
            print(f"Details: {result['algorithm_details']}")
        
        # Demo 2: Sign and Verify
        print("\n" + "="*60)
        print("  2. DIGITAL SIGNATURE & VERIFICATION")
        print("="*60)
        
        message = "demo-challenge-12345"
        for algo in ["ECDSA", "HYBRID", "ML-DSA"]:
            print(f"\n--- Signing with {algo} ---")
            sign_resp = requests.post(f"{API_BASE}/demo/sign", json={"algorithm": algo, "message": message})
            sign_result = sign_resp.json()
            print(f"Message: {sign_result['message']}")
            print(f"Public Key: {sign_result['public_key']}")
            print(f"Private Key: {sign_result['private_key'][:32]}... (truncated)")
            print(f"Signature: {sign_result['signature']}")
            print(f"Signature Size: {sign_result['signature_size_bytes']} bytes")
            
            print(f"\n--- Verifying {algo} Signature ---")
            verify_resp = requests.post(f"{API_BASE}/demo/verify", json={
                "algorithm": algo, "message": message, 
                "signature": sign_result['signature'], "public_key": sign_result['public_key'],
                "private_key": sign_result['private_key']
            })
            verify_result = verify_resp.json()
            print(f"Valid: {verify_result['valid']}")
            print(f"Details: {verify_result['details']}")
            
            # Test invalid
            print(f"\n--- Testing Invalid Signature ---")
            invalid_sig = sign_result['signature'][:-1] + ('0' if sign_result['signature'][-1] != '0' else '1')
            verify_resp2 = requests.post(f"{API_BASE}/demo/verify", json={
                "algorithm": algo, "message": message, 
                "signature": invalid_sig, "public_key": sign_result['public_key'],
                "private_key": sign_result['private_key']
            })
            verify_result2 = verify_resp2.json()
            print(f"Valid: {verify_result2['valid']}")
            print(f"Details: {verify_result2['details']}")
        
        # Demo 3: Full Flow
        print("\n" + "="*60)
        print("  3. COMPLETE IDENTITY FLOW")
        print("="*60)
        
        # Create user
        print("\n--- Step 1: Create User ---")
        user_data = {"name": "Demo User", "email": f"demo{int(time.time())}@example.com", "organization": "Skylark Drones", "password": "demo-password-123"}
        resp = requests.post(f"{API_BASE}/users", json=user_data)
        user = resp.json()
        print(f"User ID: {user['id']}")
        print(f"Name: {user['name']}")
        
        # Create identity
        print("\n--- Step 2: Create Identity (Key Generation) ---")
        identity_resp = requests.post(f"{API_BASE}/identity/create", json={"user_id": user['id'], "algorithm": "HYBRID"})
        identity = identity_resp.json()
        print(f"DID: {identity['did']}")
        print(f"Algorithm: {identity['algorithm']}")
        print(f"Public Key: {identity['public_key']}")
        print(f"Private Key (demo): {identity.get('private_key_ref', 'N/A')[:32]}...")
        print(f"Identity Hash: {identity['identity_hash']}")
        print(f"Blockchain TX: {identity['blockchain_tx'].get('tx_hash')}")
        print(f"Block: {identity['blockchain_tx'].get('block_number')}")
        
        did = identity['did']
        
        # Get challenge
        print("\n--- Step 3: Get Authentication Challenge ---")
        challenge_resp = requests.post(f"{API_BASE}/identity/authenticate/challenge?did={did}")
        challenge = challenge_resp.json()
        print(f"Challenge: {challenge['challenge']}")
        
        # Sign challenge with the identity's private key
        print("\n--- Step 4: Sign Challenge (using identity's private key) ---")
        sign_resp = requests.post(f"{API_BASE}/demo/sign-with-key", json={
            "algorithm": "HYBRID", 
            "message": challenge['challenge'],
            "private_key": identity['private_key_ref']
        })
        sign_result = sign_resp.json()
        print(f"Signature: {sign_result['signature']}")
        
        # Verify
        print("\n--- Step 5: Verify Authentication ---")
        auth_resp = requests.post(f"{API_BASE}/identity/authenticate", json={"did": did, "signature": sign_result['signature']})
        auth_result = auth_resp.json()
        print(f"Verified: {auth_result['verified']}")
        print(f"Message: {auth_result['message']}")
        print(f"Identity Status: {auth_result['identity_status']}")
        print(f"Algorithm: {auth_result.get('algorithm', 'N/A')}")
        print(f"Blockchain Verified: {auth_result.get('blockchain_verified', 'N/A')}")
        
        # Blockchain records
        print("\n--- Step 6: Blockchain Records ---")
        bc_resp = requests.get(f"{API_BASE}/blockchain/transactions?did={did}")
        bc_data = bc_resp.json()
        for tx in bc_data:
            print(f"  Block: {tx.get('block_number')} | Event: {tx.get('event_type')} | Tx: {tx.get('tx_hash')[:24]}... | Status: {tx.get('status')}")
        
        # Tamper check
        print("\n--- Step 7: Integrity/Tamper Check ---")
        tamper_resp = requests.post(f"{API_BASE}/identity/{did}/tamper-check")
        tamper = tamper_resp.json()
        print(f"Integrity Valid: {tamper['integrity_valid']}")
        print(f"Message: {tamper['message']}")
        
        # Demo 4: Benchmarks
        print("\n" + "="*60)
        print("  4. CRYPTOGRAPHIC BENCHMARKS")
        print("="*60)
        
        print("Running benchmarks (100 iterations each)...")
        resp = requests.post(f"{API_BASE}/benchmark/run", json={"iterations": 100, "operations": ["keygen", "sign", "verify"]})
        results = resp.json()
        
        print(f"\n{'Algorithm':<10} {'Operation':<12} {'Avg (ms)':<10} {'Min (ms)':<10} {'Max (ms)':<10} {'Sig Size':<10} {'Key Size':<10}")
        print("-" * 80)
        for r in results:
            print(f"{r['algorithm']:<10} {r['operation']:<12} {r['avg_time_ms']:<10.4f} {r['min_time_ms']:<10.4f} {r['max_time_ms']:<10.4f} {str(r.get('avg_signature_size', 'N/A')):<10} {str(r.get('avg_key_size', 'N/A')):<10}")
        
        # Demo 5: Quantum Readiness
        print("\n" + "="*60)
        print("  5. QUANTUM READINESS ANALYSIS")
        print("="*60)
        
        resp = requests.get(f"{API_BASE}/quantum/readiness-all")
        assessments = resp.json()
        for algo, assessment in assessments.items():
            print(f"\n--- {algo} ---")
            print(f"  Overall Score: {assessment.get('quantum_readiness_score', assessment.get('overall_score', 'N/A'))}/100")
            print(f"  Vulnerable: {assessment.get('is_vulnerable', 'N/A')}")
            print(f"  Threat: {assessment.get('quantum_threat', 'N/A')[:100]}...")
            print(f"  Recommendation: {assessment.get('recommendation', 'N/A')[:100]}...")
            if 'breakdown' in assessment:
                print(f"  Breakdown:")
                for cat, score in assessment['breakdown'].items():
                    print(f"    {cat}: {score}/100")
        
        print("\n" + "="*60)
        print("  [OK] DEMO COMPLETE")
        print("="*60)
        print("\nAll demonstrations completed successfully!")
        print("\nAccess the web UI at: http://localhost:5173")
        print("API Documentation at: http://localhost:8001/docs")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop server
        print("\nStopping server...")
        proc.terminate()
        proc.wait(timeout=5)
        print("Server stopped.")

if __name__ == "__main__":
    run_demo()