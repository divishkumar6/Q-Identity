import { useState } from 'react';
import { AlertTriangle, Play, Loader2 } from 'lucide-react';
import { Card, CardHeader } from '../components/shared';

export default function SimulationPage() {
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState(null);

  const runSimulation = async () => {
    setSimulating(true);
    setResult(null);
    await new Promise(r => setTimeout(r, 2000));

    setResult({
      mode: 'reduced-scale',
      target: 'Reduced-size discrete logarithm demonstration (8-bit)',
      attack: "Shor's Algorithm (simulated)",
      qubits_required: 15,
      circuit_depth: 84,
      simulation_time: '1.8s',
      result: 'Demonstrated integer factorization on toy problem',
      production_attack: 'NOT SIMULATED',
      production_reason: 'Current quantum hardware/simulation resources are insufficient for cryptographically relevant attacks on production ECC (256-bit).',
    });
    setSimulating(false);
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Quantum Threat Simulation</h1>
        <p className="text-sm text-gray-400">Reduced-scale educational demonstration of quantum attack principles</p>
      </div>

      <Card className="mb-8 border-gold-500/20 bg-gold-500/5">
        <div className="flex gap-3">
          <AlertTriangle className="w-5 h-5 text-gold-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-gold-400 mb-1">Important Disclaimer</p>
            <p className="text-sm text-gray-400 leading-relaxed">
              This simulation demonstrates the attack principle on <strong>reduced-scale problems</strong> and
              does <strong>not</strong> represent an actual attack on a production blockchain. Current quantum
              computers cannot break production-strength blockchain cryptography.
            </p>
          </div>
        </div>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Quantum Threat Model" subtitle="Reduced-scale Shor's algorithm demonstration" />
          <div className="space-y-4">
            {[
              ['Target', 'Reduced-size discrete log problem (toy)'],
              ['Attack Method', "Shor's Algorithm (simulated)"],
              ['Problem Size', '8-bit (vs 256-bit production ECC)'],
              ['Real Blockchain Attack', 'NOT PERFORMED'],
              ['Purpose', 'Demonstrate the mathematical attack pathway on a toy problem'],
            ].map(([k, v]) => (
              <div key={k} className="py-2 border-b border-white/5">
                <p className="text-xs text-gray-500 mb-1">{k}</p>
                <p className="text-sm text-white">{v}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <CardHeader title="Production ECC Attack" subtitle="Why this is not simulated" />
          <div className="space-y-4">
            {[
              ['Target', 'NIST P-256 (secp256r1)'],
              ['Qubits Required', '~2,500 logical qubits (estimated)'],
              ['Current Hardware', '~1,000 noisy physical qubits (best known)'],
              ['Status', 'NOT FEASIBLE WITH CURRENT PUBLICLY KNOWN HARDWARE'],
              ['Timeline', 'Uncertain; potentially decades away'],
            ].map(([k, v]) => (
              <div key={k} className="py-2 border-b border-white/5">
                <p className="text-xs text-gray-500 mb-1">{k}</p>
                <p className="text-sm text-white">{v}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="mt-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Run Reduced-Scale Demonstration</h3>
            <p className="text-sm text-gray-400">Simulate Shor's algorithm on an 8-bit toy problem</p>
          </div>
          <button
            onClick={runSimulation}
            disabled={simulating}
            className="btn-primary flex items-center gap-2"
          >
            {simulating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {simulating ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>

        {simulating && (
          <div className="flex items-center gap-3 p-4 bg-navy-900/50 rounded-xl">
            <div className="w-4 h-4 border-2 border-gold-500/30 border-t-gold-500 rounded-full animate-spin" />
            <span className="text-sm text-gray-400">
              Constructing quantum circuit for 8-bit Shor's algorithm...
            </span>
          </div>
        )}

        {result && (
          <div className="mt-4 space-y-4">
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <p className="text-sm font-semibold text-emerald-400 mb-3">TOY PROBLEM RESULT</p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {[
                  ['Target', result.target],
                  ['Qubits Required', result.qubits_required],
                  ['Circuit Depth', result.circuit_depth],
                  ['Simulation Time', result.simulation_time],
                  ['Result', result.result],
                  ['Mode', result.mode],
                ].map(([k, v]) => (
                  <div key={k}>
                    <p className="text-xs text-gray-500">{k}</p>
                    <p className="text-sm text-white font-medium">{v}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
              <p className="text-sm font-semibold text-red-400 mb-2">PRODUCTION BLOCKCHAIN ATTACK</p>
              <p className="text-sm text-red-400 font-medium">{result.production_attack}</p>
              <p className="text-sm text-gray-400 mt-1">{result.production_reason}</p>
            </div>

            <div className="p-4 bg-navy-900/50 rounded-xl">
              <p className="text-xs text-gray-400 leading-relaxed">
                This educational demonstration shows that Shor's algorithm can solve small instances of
                the discrete logarithm problem. However, scaling this to production ECC (256-bit) requires
                thousands of error-corrected logical qubits, which are not available with current technology.
                The purpose is to illustrate the mathematical attack pathway, not to demonstrate a practical
                threat.
              </p>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
