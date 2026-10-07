import { useState, useEffect } from 'react';
import { Brain, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardHeader, LoadingSpinner } from '../components/shared';

const ALGO_CONFIG = {
  ECDSA: {
    icon: 'E',
    score: 32,
    label: 'Classical',
    selectedClasses: 'border-gold-500/40 bg-gold-500/10',
    iconBg: 'bg-gold-500/15',
    iconText: 'text-gold-400',
    scoreText: 'text-gold-400',
    barColor: 'bg-gold-500',
    statusColor: 'text-gold-400',
    status: 'VULNERABLE TO FUTURE QUANTUM THREAT',
  },
  HYBRID: {
    icon: 'H',
    score: 72,
    label: 'Classical + PQC',
    selectedClasses: 'border-blue-500/40 bg-blue-500/10',
    iconBg: 'bg-blue-500/15',
    iconText: 'text-blue-400',
    scoreText: 'text-blue-400',
    barColor: 'bg-blue-500',
    statusColor: 'text-blue-400',
    status: 'HYBRID PROTECTION ACTIVE',
  },
  'ML-DSA': {
    icon: 'M',
    score: 92,
    label: 'Post-Quantum',
    selectedClasses: 'border-emerald-500/40 bg-emerald-500/10',
    iconBg: 'bg-emerald-500/15',
    iconText: 'text-emerald-400',
    scoreText: 'text-emerald-400',
    barColor: 'bg-emerald-500',
    statusColor: 'text-emerald-400',
    status: 'POST-QUANTUM READY',
  },
};

export default function QuantumReadinessPage() {
  const [assessments, setAssessments] = useState({});
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState('ECDSA');

  useEffect(() => {
    api.getAllAssessments()
      .then(setAssessments)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner text="Loading quantum readiness data..." />;

  const config = ALGO_CONFIG[selected];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Quantum Readiness Analyzer</h1>
        <p className="text-sm text-gray-400">Evaluate the quantum vulnerability of cryptographic configurations</p>
      </div>

      {/* Algorithm Selector */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {['ECDSA', 'HYBRID', 'ML-DSA'].map((algo) => {
          const d = ALGO_CONFIG[algo];
          return (
            <button
              key={algo}
              onClick={() => setSelected(algo)}
              className={`p-5 rounded-2xl border text-left transition-all ${
                selected === algo
                  ? d.selectedClasses
                  : 'border-white/5 bg-navy-800/40 hover:border-white/15'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className={`w-10 h-10 ${d.iconBg} rounded-xl flex items-center justify-center`}>
                  <span className={`text-sm font-bold ${d.iconText}`}>{d.icon}</span>
                </div>
                <span className={`text-2xl font-bold ${d.scoreText}`}>{d.score}</span>
              </div>
              <p className="text-sm font-semibold text-white">{algo}</p>
              <p className="text-xs text-gray-500 mt-1">{d.label}</p>
            </button>
          );
        })}
      </div>

      {/* Assessment Detail */}
      {assessments[selected] && (
        <div className="grid lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader
              title={`${selected} Assessment`}
              subtitle="Quantum readiness analysis based on known cryptographic assumptions"
            />
            <div className="space-y-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">Algorithm</p>
                <p className="text-sm text-white font-medium">{assessments[selected].algorithm}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Underlying Security Problem</p>
                <p className="text-sm text-gray-300">{assessments[selected].underlying_problem}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Known Quantum Threat</p>
                <p className="text-sm text-gray-300 leading-relaxed">{assessments[selected].quantum_threat}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Recommendation</p>
                <p className="text-sm text-gray-300">{assessments[selected].recommendation}</p>
              </div>
            </div>
          </Card>

          <div className="space-y-4">
            <Card>
              <CardHeader title="Quantum Readiness Score" />
              <div className="text-center py-6">
                <p className={`text-6xl font-display font-bold ${config.scoreText}`}>
                  {assessments[selected].quantum_readiness_score}
                </p>
                <p className="text-sm text-gray-500 mt-1">/ 100</p>
                <div className="mt-4 h-3 bg-navy-900 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${config.barColor} rounded-full transition-all duration-500`}
                    style={{ width: `${assessments[selected].quantum_readiness_score}%` }}
                  />
                </div>
                <p className={`mt-3 text-sm font-medium ${config.statusColor}`}>
                  {config.status}
                </p>
              </div>
            </Card>

            <Card className="border-gold-500/10">
              <div className="flex gap-3">
                <AlertTriangle className="w-5 h-5 text-gold-400 shrink-0 mt-0.5" />
                <p className="text-xs text-gray-400 leading-relaxed">
                  {assessments[selected].disclaimer}
                </p>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
