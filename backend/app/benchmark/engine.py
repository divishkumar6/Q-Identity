import statistics
import time
import hashlib
from typing import Optional

from sqlalchemy.orm import Session

from app.crypto import get_crypto_provider
from app.crypto.base import ICryptoProvider
from app.models.models import BenchmarkRun, CryptoAlgorithm
from app.core.database import SessionLocal


class BenchmarkEngine:
    """Runs cryptographic benchmarks and records results."""

    def run_benchmark(
        self,
        algorithm: str,
        iterations: int = 100,
        operations: list[str] | None = None,
        db: Session = None,
    ) -> list[dict]:
        if operations is None:
            operations = ["keygen", "sign", "verify"]

        provider = get_crypto_provider(algorithm)
        results = []

        for op in operations:
            if op == "keygen":
                result = self._benchmark_keygen(provider, algorithm, iterations)
            elif op == "sign":
                result = self._benchmark_sign(provider, algorithm, iterations)
            elif op == "verify":
                result = self._benchmark_verify(provider, algorithm, iterations)
            else:
                continue

            results.append(result)
            self._persist_result(result, db=db)

        return results

    def _benchmark_keygen(self, provider: ICryptoProvider, algorithm: str, iterations: int) -> dict:
        times = []
        key_sizes = []

        for _ in range(iterations):
            start = time.perf_counter()
            kp = provider.generate_keypair()
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            key_sizes.append(len(kp.public_key))

        return self._compute_stats("keygen", algorithm, iterations, times, avg_key_size=int(statistics.mean(key_sizes)) if key_sizes else None)

    def _benchmark_sign(self, provider: ICryptoProvider, algorithm: str, iterations: int) -> dict:
        kp = provider.generate_keypair()
        message = b"benchmark-message-for-signing-operation"
        times = []
        sig_sizes = []

        for _ in range(iterations):
            start = time.perf_counter()
            sig_result = provider.sign(kp.private_key, message)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            sig_sizes.append(sig_result.size)

        return self._compute_stats("sign", algorithm, iterations, times, avg_signature_size=int(statistics.mean(sig_sizes)) if sig_sizes else None)

    def _benchmark_verify(self, provider: ICryptoProvider, algorithm: str, iterations: int) -> dict:
        kp = provider.generate_keypair()
        message = b"benchmark-message-for-verification-operation"
        sig_result = provider.sign(kp.private_key, message)
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            provider.verify(kp.public_key, message, sig_result.signature)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        return self._compute_stats("verify", algorithm, iterations, times)

    def _compute_stats(
        self,
        operation: str,
        algorithm: str,
        iterations: int,
        times: list[float],
        avg_signature_size: Optional[int] = None,
        avg_key_size: Optional[int] = None,
    ) -> dict:
        return {
            "algorithm": algorithm,
            "operation": operation,
            "iterations": iterations,
            "avg_time_ms": round(statistics.mean(times), 4),
            "min_time_ms": round(min(times), 4),
            "max_time_ms": round(max(times), 4),
            "median_time_ms": round(statistics.median(times), 4),
            "std_dev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0.0,
            "avg_signature_size": avg_signature_size,
            "avg_key_size": avg_key_size,
        }

    def _persist_result(self, result: dict, db: Session = None):
        try:
            algo_map = {"ECDSA": CryptoAlgorithm.ECDSA, "HYBRID": CryptoAlgorithm.HYBRID, "ML-DSA": CryptoAlgorithm.MLDSA}
            close_db = False
            if db is None:
                db = SessionLocal()
                close_db = True
            run = BenchmarkRun(
                algorithm=algo_map.get(result["algorithm"], CryptoAlgorithm.ECDSA),
                iterations=result["iterations"],
                operation=result["operation"],
                avg_time_ms=result["avg_time_ms"],
                min_time_ms=result["min_time_ms"],
                max_time_ms=result["max_time_ms"],
                median_time_ms=result["median_time_ms"],
                std_dev_ms=result["std_dev_ms"],
                avg_signature_size=result.get("avg_signature_size"),
                avg_key_size=result.get("avg_key_size"),
            )
            db.add(run)
            db.commit()
            db.close()
        except Exception:
            pass

    def get_historical_results(self, algorithm: Optional[str] = None, limit: int = 50, db: Session = None) -> list[dict]:
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            query = db.query(BenchmarkRun)
            if algorithm:
                algo_map = {"ECDSA": CryptoAlgorithm.ECDSA, "HYBRID": CryptoAlgorithm.HYBRID, "ML-DSA": CryptoAlgorithm.MLDSA}
                query = query.filter(BenchmarkRun.algorithm == algo_map.get(algorithm, CryptoAlgorithm.ECDSA))
            runs = query.order_by(BenchmarkRun.id.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "algorithm": r.algorithm.value,
                    "operation": r.operation,
                    "iterations": r.iterations,
                    "avg_time_ms": r.avg_time_ms,
                    "min_time_ms": r.min_time_ms,
                    "max_time_ms": r.max_time_ms,
                    "median_time_ms": r.median_time_ms,
                    "std_dev_ms": r.std_dev_ms,
                    "avg_signature_size": r.avg_signature_size,
                    "avg_key_size": r.avg_key_size,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in runs
            ]
        finally:
            if close_db:
                db.close()


benchmark_engine = BenchmarkEngine()
