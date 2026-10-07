import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle2, XCircle, Loader2, ArrowLeft, Copy, Key, Hash, Shield, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardHeader, LoadingSpinner } from '../components/shared';

export default function VerificationResultPage() {
  const { did, verified } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [showPrivateKey, setShowPrivateKey] = useState(false);

  const isVerified = verified === 'success';

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const identity = await api.getIdentity(did);
        setData(identity);
      } catch (e) {
        setError('Failed to load identity details');
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [did]);

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  if (loading) return <LoadingSpinner text="Loading verification details..." />;
  if (error || !data) return (
    <div className="text-center py-12">
      <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
      <p className="text-gray-400">{error || 'Verification details not found'}</p>
      <button onClick={() => navigate('/app/authenticate')} className="btn-secondary mt-4 text-sm">Back to Authentication</button>
    </div>
  );

  return (
    <div>
      <div className="mb-8">
        <button onClick={() => navigate('/app/authenticate')} className="btn-secondary text-sm flex items-center gap-2 mb-4">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h1 className="text-2xl font-display font-bold text-white mb-2">
          {isVerified ? 'Successful Verification' : 'Failed Verification'}
        </h1>
        <p className="text-sm text-gray-400">Detailed verification result for identity {did.slice(0, 16)}...</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className={isVerified ? 'border-emerald-500/20' : 'border-red-500/20'}>
            <CardHeader
              title={isVerified ? 'Verification Successful ✓' : 'Verification Failed ✗'}
              subtitle={isVerified ? 'Identity authenticated and verified on blockchain' : 'Authentication failed - invalid signature or identity issue'}
              action={
                <button onClick={() => setShowDetails(!showDetails)} className="btn-outline text-sm py-2">
                  {showDetails ? 'Hide Details' : 'Show Details'}
                </button>
              }
            />
            
            <div className={`flex items-center gap-4 p-4 rounded-xl ${isVerified ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}>
              {isVerified ? (
                <CheckCircle2 className="w-10 h-10 text-emerald-400" />
              ) : (
                <XCircle className="w-10 h-10 text-red-400" />
              )}
              <div>
                <h3 className={`text-lg font-bold ${isVerified ? 'text-emerald-400' : 'text-red-400'}`}>
                  {isVerified ? 'IDENTITY VERIFIED' : 'AUTHENTICATION FAILED'}
                </h3>
                <p className="text-sm text-gray-400 mt-1">
                  {isVerified 
                    ? 'The cryptographic signature is valid. Identity is active and verified on blockchain.'
                    : 'The signature verification failed. Identity may be revoked, expired, or signature is invalid.'
                  }
                </p>
              </div>
            </div>

            {showDetails && (
              <div className="space-y-4 mt-4 pt-4 border-t border-white/5">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    ['Status', isVerified ? 'VERIFIED' : 'FAILED', isVerified ? 'text-emerald-400' : 'text-red-400'],
                    ['Identity', data.status.toUpperCase(), data.status === 'active' ? 'text-emerald-400' : 'text-gray-400'],
                    ['Algorithm', data.algorithm, 'text-blue-400'],
                    ['Blockchain', data.blockchain_tx_hash ? 'VERIFIED' : 'NOT ON CHAIN', data.blockchain_tx_hash ? 'text-emerald-400' : 'text-gray-400'],
                  ].map(([k, v, c]) => (
                    <div key={k} className="bg-navy-800/50 p-4 rounded-xl text-center">
                      <p className="text-xs text-gray-500 mb-1">{k}</p>
                      <p className={`text-sm font-bold ${c}`}>{v}</p>
                    </div>
                  ))}
                </div>

                <div className="space-y-3">
                  <p className="text-xs text-gray-500">Identity Hash</p>
                  <div className="bg-navy-900/50 p-3 rounded-xl flex items-center justify-between">
                    <p className="text-xs font-mono text-gray-300 break-all">{data.identity_hash}</p>
                    <button onClick={() => copyToClipboard(data.identity_hash, 'Identity hash')} className="btn-outline text-xs">
                      <Copy className="w-3 h-3" /> Copy
                    </button>
                  </div>
                </div>

                {data.blockchain_tx_hash && (
                  <div className="space-y-3">
                    <p className="text-xs text-gray-500">Blockchain Transaction</p>
                    <div className="bg-navy-900/50 p-3 rounded-xl flex items-center justify-between">
                      <p className="text-xs font-mono text-gold-400 break-all">{data.blockchain_tx_hash}</p>
                    </div>
                    <p className="text-xs text-gray-500">Block: {data.blockchain_block_number}</p>
                  </div>
                )}
              </div>
            )}
          </Card>

          {isVerified && data && (
            <Card>
              <CardHeader title="Cryptographic Verification Details" />
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-navy-800/50 p-4 rounded-xl">
                    <p className="text-xs text-gray-500 mb-1">Public Key</p>
                    <p className="text-xs font-mono text-white break-all">{data.public_key}</p>
                  </div>
                  <div className="bg-navy-800/50 p-4 rounded-xl">
                    <p className="text-xs text-gray-500 mb-1">Security Level</p>
                    <p className="text-lg font-bold text-gold-400">{data.security_level}</p>
                  </div>
                </div>

                <div className="bg-navy-900/50 p-4 rounded-xl">
                  <p className="text-xs text-gray-500 mb-2">Verification Process</p>
                  <div className="space-y-2 text-xs">
                    {[
                      '1. Server received challenge-response authentication request',
                      '2. Retrieved identity public key from database',
                      '3. Verified ECDSA/ML-DSA signature against challenge',
                      '4. Confirmed identity status is ACTIVE',
                      '5. Validated blockchain record exists and matches',
                      '6. Returned verification result: SUCCESS',
                    ].map((step, i) => (
                      <div key={i} className="flex items-center gap-2 text-green-400">
                        <span className="w-4 h-4 bg-emerald-500 rounded-full flex items-center justify-center shrink-0">
                          <span className="text-[10px] font-bold text-white">{i + 1}</span>
                        </span>
                        <span className="text-gray-300">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          )}

          {!isVerified && (
            <Card className="border-red-500/20">
              <CardHeader title="Failure Analysis" />
              <div className="space-y-4">
                <div className="bg-red-500/10 p-4 rounded-xl border border-red-500/20">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="w-6 h-6 text-red-400" />
                    <div>
                      <p className="font-medium text-red-400">Authentication Failed</p>
                      <p className="text-sm text-gray-400">The signature could not be verified with the stored public key.</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  {[
                    ['Possible Causes', [
                      'Invalid or corrupted signature',
                      'Wrong private key used for signing',
                      'Identity has been revoked',
                      'Challenge has expired',
                      'Identity not found or inactive',
                    ]],
                    ['Troubleshooting', [
                      'Ensure the correct DID is being used',
                      'Verify the identity is active (not revoked)',
                      'Check that the challenge has not expired (30s default)',
                      'Confirm the correct algorithm is being used',
                    ]],
                  ].map(([title, items]) => (
                    <div key={title} className="bg-navy-800/50 p-4 rounded-xl">
                      <p className="text-xs text-gray-500 mb-2 font-medium">{title}</p>
                      <ul className="space-y-1 text-xs text-gray-400">
                        {items.map((item, i) => (
                          <li key={i} className="flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-red-400 rounded-full" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          )}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader title="Identity Summary" />
            <div className="space-y-3">
              {[
                ['DID', data.did],
                ['Algorithm', data.algorithm],
                ['Status', data.status.toUpperCase()],
                ['Security Level', data.security_level],
                ['Created', data.created_at ? new Date(data.created_at).toLocaleDateString() : 'N/A'],
                ['Blockchain', data.blockchain_tx_hash ? 'Registered' : 'Not Registered'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-sm text-gray-400">{k}</span>
                  <span className="text-sm text-white font-mono text-xs">{v}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <CardHeader title="Actions" />
            <div className="space-y-2">
              <button onClick={() => navigate(`/app/identity/${did}`)} className="w-full btn-primary text-sm py-2">
                <Shield className="w-4 h-4 mr-2" /> View Full Identity
              </button>
              <button onClick={() => navigate('/app/authenticate')} className="w-full btn-secondary text-sm py-2">
                <ArrowLeft className="w-4 h-4 mr-2" /> Try Another Authentication
              </button>
              <button onClick={() => navigate('/app/blockchain')} className="w-full btn-outline text-sm py-2">
                <Hash className="w-4 h-4 mr-2" /> View Blockchain Records
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}