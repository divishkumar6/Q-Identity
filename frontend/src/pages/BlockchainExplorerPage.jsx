import { useState, useEffect } from 'react';
import { Link2, Copy, FileText, Search, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardHeader, LoadingSpinner, EmptyState, StatusBadge } from '../components/shared';

export default function BlockchainExplorerPage() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState(null);
  const [showRaw, setShowRaw] = useState(false);

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  useEffect(() => {
    api.getBlockchainTransactions()
      .then((data) => setTransactions(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load blockchain data'))
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter
    ? transactions.filter((t) => t.event_type?.includes(filter) || t.identity_did?.includes(filter))
    : transactions;

  if (loading) return <LoadingSpinner text="Loading blockchain data..." />;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Blockchain Explorer</h1>
        <p className="text-sm text-gray-400">View all blockchain transactions and identity records</p>
      </div>

      {error && (
        <Card className="mb-6 border-red-500/20">
          <p className="text-sm text-red-400">{error}</p>
        </Card>
      )}

      <div className="mb-6 flex gap-3 flex-wrap">
        {['', 'identity_registered', 'migration_recorded', 'identity_revoked'].map((f) => (
          <button
            key={f}
            onClick={() => { setFilter(f); setSelected(null); }}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              filter === f ? 'bg-gold-500/15 text-gold-400 border border-gold-500/20' : 'bg-navy-800/40 text-gray-400 border border-white/5 hover:border-white/15'
            }`}
          >
            {f || 'All'}
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {filtered.length === 0 ? (
            <EmptyState icon={<Link2 className="w-12 h-12" />} title="No Transactions" description="Create an identity to see blockchain transactions." />
          ) : (
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5">
                      <th className="text-left py-3 text-gray-500 font-medium">Block</th>
                      <th className="text-left py-3 text-gray-500 font-medium">Event</th>
                      <th className="text-left py-3 text-gray-500 font-medium">DID</th>
                      <th className="text-left py-3 text-gray-500 font-medium">Status</th>
                      <th className="text-left py-3 text-gray-500 font-medium">Tx Hash</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((tx, i) => (
                      <tr
                        key={i}
                        onClick={() => setSelected(tx)}
                        className={`border-b border-white/3 cursor-pointer transition-colors ${
                          selected?.tx_hash === tx.tx_hash ? 'bg-gold-500/5' : 'hover:bg-white/3'
                        }`}
                      >
                        <td className="py-3 text-gray-300">{tx.block_number || '—'}</td>
                        <td className="py-3 text-gray-300">{tx.event_type}</td>
                        <td className="py-3 text-gray-400 font-mono text-xs">{tx.identity_did?.slice(0, 16)}...</td>
                        <td className="py-3"><StatusBadge status={tx.status} /></td>
                        <td className="py-3 text-gray-400 font-mono text-xs">{tx.tx_hash?.slice(0, 16)}...</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>

        <div>
          {selected ? (
            <Card>
              <div className="flex items-center justify-between mb-4">
                <CardHeader title="Transaction Details" />
                <div className="flex gap-2">
                  <button onClick={() => copyToClipboard(selected.tx_hash, 'Tx hash')} className="btn-outline text-xs flex items-center gap-1">
                    <Copy className="w-3 h-3" /> Copy Hash
                  </button>
                  <button onClick={() => setShowRaw(!showRaw)} className="btn-outline text-xs flex items-center gap-1">
                    {showRaw ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    {showRaw ? ' Hide Raw' : ' Show Raw'}
                  </button>
                </div>
              </div>
              <div className="space-y-3">
                {[
                  ['Tx Hash', selected.tx_hash],
                  ['Block', selected.block_number],
                  ['Event', selected.event_type],
                  ['DID', selected.identity_did],
                  ['Payload Hash', selected.payload_hash],
                  ['Gas Used', selected.gas_used],
                  ['Status', selected.status],
                  ['Timestamp', selected.created_at ? new Date(selected.created_at).toLocaleString() : 'N/A'],
                ].map(([k, v]) => (
                  <div key={k} className="py-2 border-b border-white/5">
                    <p className="text-xs text-gray-500 mb-1">{k}</p>
                    <p className="text-sm text-white font-mono break-all">{v || '—'}</p>
                  </div>
                ))}
              </div>
              {showRaw && (
                <div className="mt-4 p-4 bg-navy-900/50 rounded-xl">
                  <p className="text-xs text-gray-500 mb-2">Raw Transaction Data</p>
                  <pre className="text-xs font-mono text-gray-300 overflow-auto max-h-64">{JSON.stringify(selected, null, 2)}</pre>
                </div>
              )}
            </Card>
          ) : (
            <Card>
              <p className="text-sm text-gray-500 text-center py-8">Select a transaction to view details</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
