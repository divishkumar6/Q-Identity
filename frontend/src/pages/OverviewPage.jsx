import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, Shield, ArrowRightLeft, ChevronRight, Link2, Brain } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardHeader, LoadingSpinner, StatusBadge } from '../components/shared';

export default function OverviewPage() {
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api.getResearchSummary().catch(() => null),
      api.getBlockchainTransactions().catch(() => []),
    ])
      .then(([s, t]) => {
        setSummary(s);
        setTransactions(Array.isArray(t) ? t.slice(0, 8) : []);
      })
      .catch(() => setError('Failed to load data'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner text="Loading dashboard..." />;

  if (error) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-display font-bold text-white mb-2">Overview</h1>
          <p className="text-sm text-gray-400">Quantum readiness at a glance</p>
        </div>
        <Card>
          <p className="text-red-400 text-sm">{error}. Make sure the backend is running on port 8001.</p>
        </Card>
      </div>
    );
  }

  const stats = [
    { label: 'Total Identities', value: summary?.total_identities || 0, icon: Users, color: 'text-gold-400' },
    { label: 'Active Identities', value: summary?.active_identities || 0, icon: Shield, color: 'text-emerald-400' },
    { label: 'PQC Identities', value: summary?.pqc_identities || 0, icon: Brain, color: 'text-blue-400' },
    { label: 'Blockchain Txns', value: summary?.total_transactions || 0, icon: Link2, color: 'text-purple-400' },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Overview</h1>
        <p className="text-sm text-gray-400">Quantum readiness at a glance</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((s, i) => (
          <Card key={i}>
            <div className="flex items-start justify-between">
              <div>
                <p className="stat-label">{s.label}</p>
                <p className="stat-value mt-1">{s.value}</p>
              </div>
              <s.icon className={`w-5 h-5 ${s.color} opacity-60`} />
            </div>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-4 mb-8">
        <Card>
          <p className="stat-label mb-3">Classical (ECDSA)</p>
          <div className="flex items-end justify-between">
            <p className="text-2xl font-bold text-white">{summary?.classical_identities || 0}</p>
            <div className="text-right">
              <p className="text-xs text-gray-500">QR Score</p>
              <p className="text-lg font-bold text-gold-400">32/100</p>
            </div>
          </div>
          <div className="mt-3 h-1.5 bg-navy-900 rounded-full overflow-hidden">
            <div className="h-full bg-gold-500 rounded-full" style={{ width: '32%' }} />
          </div>
        </Card>
        <Card>
          <p className="stat-label mb-3">Hybrid</p>
          <div className="flex items-end justify-between">
            <p className="text-2xl font-bold text-white">{summary?.hybrid_identities || 0}</p>
            <div className="text-right">
              <p className="text-xs text-gray-500">QR Score</p>
              <p className="text-lg font-bold text-blue-400">72/100</p>
            </div>
          </div>
          <div className="mt-3 h-1.5 bg-navy-900 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: '72%' }} />
          </div>
        </Card>
        <Card>
          <p className="stat-label mb-3">Post-Quantum (ML-DSA)</p>
          <div className="flex items-end justify-between">
            <p className="text-2xl font-bold text-white">{summary?.pqc_identities || 0}</p>
            <div className="text-right">
              <p className="text-xs text-gray-500">QR Score</p>
              <p className="text-lg font-bold text-emerald-400">92/100</p>
            </div>
          </div>
          <div className="mt-3 h-1.5 bg-navy-900 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-500 rounded-full" style={{ width: '92%' }} />
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader
          title="Recent Blockchain Activity"
          action={
            <Link to="/app/blockchain" className="text-gold-400 text-sm flex items-center gap-1 hover:underline">
              View All <ChevronRight className="w-3 h-3" />
            </Link>
          }
        />
        {transactions.length === 0 ? (
          <p className="text-gray-500 text-sm py-4">No blockchain transactions yet. Create an identity to get started.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left py-3 text-gray-500 font-medium">Event</th>
                  <th className="text-left py-3 text-gray-500 font-medium">DID</th>
                  <th className="text-left py-3 text-gray-500 font-medium">Status</th>
                  <th className="text-left py-3 text-gray-500 font-medium">Tx Hash</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx, i) => (
                  <tr key={i} className="border-b border-white/3">
                    <td className="py-3 text-gray-300">{tx.event_type}</td>
                    <td className="py-3 text-gray-400 font-mono text-xs">{tx.identity_did?.slice(0, 20)}...</td>
                    <td className="py-3"><StatusBadge status={tx.status} /></td>
                    <td className="py-3 text-gray-400 font-mono text-xs">{tx.tx_hash?.slice(0, 16)}...</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
