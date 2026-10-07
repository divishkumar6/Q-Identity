import { useState, useEffect } from 'react';
import { ArrowRightLeft, Loader2, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardHeader, LoadingSpinner, AlgorithmBadge } from '../components/shared';

export default function MigrationPage() {
  const [identities, setIdentities] = useState([]);
  const [selectedDid, setSelectedDid] = useState('');
  const [targetAlgo, setTargetAlgo] = useState('ML-DSA');
  const [loading, setLoading] = useState(true);
  const [migrating, setMigrating] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.listIdentities()
      .then((ids) => {
        const list = Array.isArray(ids) ? ids : [];
        setIdentities(list);
        if (list.length > 0) setSelectedDid(list[0].did);
      })
      .catch(() => setError('Failed to load identities'))
      .finally(() => setLoading(false));
  }, []);

  const loadHistory = async (did) => {
    try {
      const h = await api.getMigrationHistory(did);
      setHistory(Array.isArray(h) ? h : []);
    } catch { setHistory([]); }
  };

  useEffect(() => {
    if (selectedDid) loadHistory(selectedDid);
  }, [selectedDid]);

  const handleMigrate = async () => {
    if (!selectedDid) return;
    setMigrating(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.migrate({ did: selectedDid, target_algorithm: targetAlgo });
      setResult(res);
      await loadHistory(selectedDid);
    } catch (e) {
      setError(e.message || 'Migration failed');
    } finally {
      setMigrating(false);
    }
  };

  if (loading) return <LoadingSpinner text="Loading identities..." />;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">PQC Migration</h1>
        <p className="text-sm text-gray-400">Migrate identity cryptographic keys from classical to post-quantum</p>
      </div>

      {error && (
        <Card className="mb-6 border-red-500/20">
          <p className="text-sm text-red-400">{error}</p>
        </Card>
      )}

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <Card>
            <CardHeader title="Migration Configuration" subtitle="Select identity and target algorithm" />
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Select Identity</label>
                <select
                  className="input-field"
                  value={selectedDid}
                  onChange={(e) => setSelectedDid(e.target.value)}
                >
                  {identities.length === 0 && <option value="">No identities available</option>}
                  {identities.map((id) => (
                    <option key={id.did} value={id.did}>{id.did.slice(0, 30)}... ({id.algorithm})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3">Target Algorithm</label>
                <div className="grid grid-cols-3 gap-3">
                  {['ECDSA', 'HYBRID', 'ML-DSA'].map((algo) => (
                    <button
                      key={algo}
                      onClick={() => setTargetAlgo(algo)}
                      className={`p-3 rounded-xl border text-center text-sm font-medium transition-all ${
                        targetAlgo === algo
                          ? 'border-gold-500/40 bg-gold-500/10 text-gold-400'
                          : 'border-white/10 text-gray-400 hover:border-white/20'
                      }`}
                    >
                      {algo}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleMigrate}
                disabled={migrating || !selectedDid}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {migrating ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Migrating...</>
                ) : (
                  <><ArrowRightLeft className="w-4 h-4" /> Migrate to {targetAlgo}</>
                )}
              </button>
            </div>
          </Card>

          {result && (
            <Card className="border-emerald-500/20">
              <CardHeader title="Migration Complete" />
              <div className="space-y-3">
                {(result.steps || []).map((step, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                    <div>
                      <p className="text-sm text-white">Step {step.step}: {step.description}</p>
                      <p className="text-xs text-emerald-400">{step.status}</p>
                    </div>
                  </div>
                ))}
              </div>
              {result.blockchain_tx && (
                <div className="mt-4 p-3 bg-navy-900/50 rounded-xl">
                  <p className="text-xs text-gray-500">Blockchain Transaction</p>
                  <p className="text-xs font-mono text-gold-400 break-all">{result.blockchain_tx.tx_hash}</p>
                </div>
              )}
            </Card>
          )}
        </div>

        <Card>
          <CardHeader title="Migration History" subtitle={`For ${selectedDid?.slice(0, 24)}...`} />
          {history.length === 0 ? (
            <p className="text-sm text-gray-500 py-4">No migrations recorded for this identity.</p>
          ) : (
            <div className="space-y-4">
              {history.map((h, i) => (
                <div key={i} className="flex items-start gap-4 p-4 bg-navy-900/30 rounded-xl">
                  <div className="w-8 h-8 bg-blue-500/15 rounded-lg flex items-center justify-center shrink-0">
                    <span className="text-xs font-bold text-blue-400">{i + 1}</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <AlgorithmBadge algorithm={h.old_algorithm} />
                      <span className="text-gray-500">&rarr;</span>
                      <AlgorithmBadge algorithm={h.new_algorithm} />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {h.created_at ? new Date(h.created_at).toLocaleString() : 'N/A'}
                    </p>
                    {h.blockchain_tx_hash && (
                      <p className="text-xs font-mono text-gray-400 mt-1 break-all">
                        Tx: {h.blockchain_tx_hash.slice(0, 24)}...
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
