import { useState, useEffect } from 'react';
import { BookOpen, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardHeader, LoadingSpinner } from '../components/shared';

export default function ResearchPage() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getResearchSummary()
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner text="Loading research data..." />;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Research Findings</h1>
        <p className="text-sm text-gray-400">Experimental comparison of classical, hybrid, and post-quantum cryptography</p>
      </div>

      <Card className="mb-8">
        <CardHeader title="Research Problem" icon={<BookOpen className="w-5 h-5 text-gold-400" />} />
        <div className="space-y-4 text-sm text-gray-300 leading-relaxed">
          <p>
            Classical public-key cryptography (specifically ECDSA) used by blockchain-based identity systems
            may be threatened by future cryptographically relevant quantum computers. Shor's algorithm, when
            run on a sufficiently large quantum computer, could solve the Elliptic Curve Discrete Logarithm
            Problem (ECDLP) in polynomial time.
          </p>
          <p>
            However, current quantum hardware is far from capable of executing such an attack on production
            blockchain systems. This project addresses the <strong className="text-gold-400">future quantum threat</strong> and studies the
            practical migration of blockchain-based identity systems toward post-quantum cryptography.
          </p>
        </div>
      </Card>

      <Card className="mb-8">
        <CardHeader title="Approach" />
        <div className="grid md:grid-cols-3 gap-6">
          <div className="p-5 bg-gold-500/5 border border-gold-500/15 rounded-xl">
            <h3 className="text-sm font-semibold text-gold-400 mb-2">Crypto-Agility Layer</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Abstract cryptographic operations behind a common interface, allowing seamless switching between algorithms without changing the identity workflow.
            </p>
          </div>
          <div className="p-5 bg-blue-500/5 border border-blue-500/15 rounded-xl">
            <h3 className="text-sm font-semibold text-blue-400 mb-2">Quantum Readiness Assessment</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Transparent scoring system based on known cryptographic assumptions, quantum attack applicability, and NIST standardization status.
            </p>
          </div>
          <div className="p-5 bg-emerald-500/5 border border-emerald-500/15 rounded-xl">
            <h3 className="text-sm font-semibold text-emerald-400 mb-2">Performance Benchmarking</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Real measurements of key generation, signing, verification latency, signature sizes, and blockchain transaction overhead across all three modes.
            </p>
          </div>
        </div>
      </Card>

      <Card className="mb-8">
        <CardHeader title="Algorithms Under Comparison" />
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left py-3 text-gray-500 font-medium">Property</th>
                <th className="text-left py-3 text-gold-400 font-medium">ECDSA</th>
                <th className="text-left py-3 text-blue-400 font-medium">Hybrid</th>
                <th className="text-left py-3 text-emerald-400 font-medium">ML-DSA</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['Type', 'Classical', 'Classical + PQC', 'Post-Quantum'],
                ['Standard', 'NIST FIPS 186-5', 'Combined', 'NIST FIPS 204'],
                ['Security Basis', 'ECDLP', 'ECDLP + MLWE/Module-SIS', 'MLWE / Module-SIS'],
                ['Quantum Vulnerable', 'Yes (Shor)', 'ECDSA component only', 'No known quantum attack'],
                ['Sig Size', '~72 bytes', '~3381 bytes', '~3309 bytes'],
                ['Key Size', '~91 bytes', '~2043 bytes', '~1952 bytes'],
                ['QR Score', '32/100', '72/100', '92/100'],
              ].map(([prop, ...vals], i) => (
                <tr key={i} className="border-b border-white/3">
                  <td className="py-3 text-gray-300 font-medium">{prop}</td>
                  {vals.map((v, j) => (
                    <td key={j} className="py-3 text-gray-400">{v}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {summary && (
        <Card className="mb-8">
          <CardHeader title="Current Experiment Data" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              ['Total Identities', summary.total_identities],
              ['Classical', summary.classical_identities],
              ['Hybrid', summary.hybrid_identities],
              ['Post-Quantum', summary.pqc_identities],
              ['Active', summary.active_identities],
              ['Revoked', summary.revoked_identities],
              ['Migrated', summary.migrated_identities],
              ['Blockchain Txns', summary.total_transactions],
            ].map(([label, value]) => (
              <div key={label} className="p-4 bg-navy-900/30 rounded-xl">
                <p className="text-xs text-gray-500">{label}</p>
                <p className="text-xl font-bold text-white mt-1">{value}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card className="border-gold-500/10">
        <div className="flex gap-3">
          <AlertTriangle className="w-5 h-5 text-gold-400 shrink-0 mt-0.5" />
          <div className="text-sm text-gray-400 leading-relaxed">
            <p className="font-semibold text-gold-400 mb-2">Limitations & Honest Assessment</p>
            <ul className="space-y-2 list-disc list-inside">
              <li>Current quantum hardware is NOT used to claim a real production blockchain break.</li>
              <li>ML-DSA security is based on well-studied lattice assumptions, not proven unbreakability.</li>
              <li>Benchmark results reflect the prototype implementation, not optimized production code.</li>
              <li>Blockchain transaction costs are simulated in a local development environment.</li>
              <li>Signature sizes for ML-DSA are larger than ECDSA - this is a real trade-off.</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}
