import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Shield, Brain, ArrowRightLeft, Trash2,
  CheckCircle2, Copy
} from 'lucide-react';
import { api } from '../services/api';
import { Card, CardHeader, LoadingSpinner, StatusBadge, AlgorithmBadge } from '../components/shared';

export default function IdentityDetailPage() {
  const { did } = useParams();
  const navigate = useNavigate();
  const [identity, setIdentity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tamperResult, setTamperResult] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api.getIdentity(did)
      .then(setIdentity)
      .catch(() => setError('Identity not found or backend is not running'))
      .finally(() => setLoading(false));
  }, [did]);

  const handleTamperCheck = async () => {
    try {
      const result = await api.tamperCheck(did);
      setTamperResult(result);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRevoke = async () => {
    if (!confirm('Are you sure you want to revoke this identity?')) return;
    try {
      await api.revoke({ did, reason: 'User-initiated revocation' });
      const updated = await api.getIdentity(did);
      setIdentity(updated);
    } catch (e) {
      console.error(e);
    }
  };

  const copyDid = () => {
    navigator.clipboard.writeText(did);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) return <LoadingSpinner text="Loading identity..." />;
  if (error || !identity) return (
    <div className="text-center py-12">
      <p className="text-gray-400">{error || 'Identity not found'}</p>
      <button onClick={() => navigate('/app/identities')} className="btn-secondary mt-4 text-sm">Back to Identities</button>
    </div>
  );

  const qrScore = identity.algorithm === 'ECDSA' ? 32 : identity.algorithm === 'HYBRID' ? 72 : 92;
  const qrBarClass = identity.algorithm === 'ECDSA' ? 'bg-gold-500' : identity.algorithm === 'HYBRID' ? 'bg-blue-500' : 'bg-emerald-500';

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Identity Detail</h1>
        <p className="text-sm text-gray-400">Complete information about this decentralized identity</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader title="Identity Information" />
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-gray-500 mb-1">DID</p>
                  <p className="text-sm font-mono text-white break-all">{identity.did}</p>
                </div>
                <button onClick={copyDid} className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                  <Copy className="w-4 h-4 text-gray-400" />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Status</p>
                  <StatusBadge status={identity.status} />
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Algorithm</p>
                  <AlgorithmBadge algorithm={identity.algorithm} />
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Security Level</p>
                  <p className="text-sm text-white">{identity.security_level || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Created</p>
                  <p className="text-sm text-white">{identity.created_at ? new Date(identity.created_at).toLocaleDateString() : 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Last Migration</p>
                  <p className="text-sm text-white">{identity.last_migration_at ? new Date(identity.last_migration_at).toLocaleDateString() : 'Never'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Block</p>
                  <p className="text-sm text-white">{identity.blockchain_block_number || 'N/A'}</p>
                </div>
              </div>

              <div>
                <p className="text-xs text-gray-500 mb-1">Identity Hash</p>
                <p className="text-xs font-mono text-gray-400 break-all bg-navy-900/50 p-3 rounded-lg">
                  {identity.identity_hash}
                </p>
              </div>

              {identity.blockchain_tx_hash && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">Blockchain Transaction</p>
                  <p className="text-xs font-mono text-gold-400 break-all">{identity.blockchain_tx_hash}</p>
                </div>
              )}
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Integrity Verification"
              subtitle="Verify that identity data has not been tampered with"
              action={
                <button onClick={handleTamperCheck} className="btn-outline text-sm py-2">
                  Run Check
                </button>
              }
            />
            {tamperResult && (
              <div className={`p-4 rounded-xl ${tamperResult.integrity_valid ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                <div className="flex items-center gap-2 mb-2">
                  {tamperResult.integrity_valid ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <span className="text-red-400 text-lg">✕</span>
                  )}
                  <span className={`font-semibold ${tamperResult.integrity_valid ? 'text-emerald-400' : 'text-red-400'}`}>
                    {tamperResult.integrity_valid ? 'INTEGRITY VERIFIED' : 'INTEGRITY CHECK FAILED'}
                  </span>
                </div>
                <p className="text-sm text-gray-400">{tamperResult.message}</p>
                <div className="mt-3 grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <p className="text-gray-500">Original Hash</p>
                    <p className="font-mono text-gray-300 break-all">{tamperResult.original_hash?.slice(0, 32)}...</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Current Hash</p>
                    <p className="font-mono text-gray-300 break-all">{tamperResult.current_hash?.slice(0, 32)}...</p>
                  </div>
                </div>
              </div>
            )}
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader title="Actions" />
            <div className="space-y-3">
              <button
                onClick={() => navigate('/app/authenticate')}
                className="w-full btn-primary flex items-center justify-center gap-2 text-sm py-2.5"
              >
                <Shield className="w-4 h-4" /> Authenticate
              </button>
              <button
                onClick={() => navigate('/app/quantum')}
                className="w-full btn-secondary flex items-center justify-center gap-2 text-sm py-2.5"
              >
                <Brain className="w-4 h-4" /> Analyze Quantum Readiness
              </button>
              <button
                onClick={() => navigate('/app/migration')}
                className="w-full btn-secondary flex items-center justify-center gap-2 text-sm py-2.5"
              >
                <ArrowRightLeft className="w-4 h-4" /> Migrate to PQC
              </button>
              <button
                onClick={handleRevoke}
                disabled={identity.status === 'revoked'}
                className="w-full btn-danger flex items-center justify-center gap-2 text-sm py-2.5 disabled:opacity-40"
              >
                <Trash2 className="w-4 h-4" /> Revoke Identity
              </button>
            </div>
          </Card>

          <Card>
            <CardHeader title="Quantum Readiness" />
            <div className="text-center py-4">
              <p className="text-4xl font-bold text-gold-400">{qrScore}</p>
              <p className="text-xs text-gray-500 mt-1">/ 100</p>
              <div className="mt-3 h-2 bg-navy-900 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${qrBarClass}`} style={{ width: `${qrScore}%` }} />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {identity.algorithm === 'ECDSA' ? 'Vulnerable to future quantum threat' :
                 identity.algorithm === 'HYBRID' ? 'Hybrid protection active' :
                 'Post-quantum ready'}
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
