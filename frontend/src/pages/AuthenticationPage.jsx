import { useState } from 'react';
import { Shield, Loader2, CheckCircle2, XCircle, Key, Copy, Hash, Signature, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Card, CardHeader } from '../components/shared';

export default function AuthenticationPage() {
  const navigate = useNavigate();
  const [did, setDid] = useState('');
  const [step, setStep] = useState(0);
  const [challenge, setChallenge] = useState(null);
  const [result, setResult] = useState(null);
  const [signatureData, setSignatureData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const steps = ['Requesting challenge...', 'Signing challenge...', 'Verifying signature...'];

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  const handleRequestChallenge = async () => {
    if (!did.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setChallenge(null);
    setSignatureData(null);
    try {
      setStep(0);
      const res = await api.getChallenge(did);
      setChallenge(res);
      setStep(1);

      await new Promise(r => setTimeout(r, 500));
      
      // Get identity to find algorithm and retrieve stored private key
      const identity = await api.getIdentity(did);
      const algorithm = identity.algorithm;
      const storedPrivateKey = localStorage.getItem(`qidentity_private_key_${did}`);
      
      if (!storedPrivateKey) {
        throw new Error(`No private key found for DID ${did}. Please create the identity first or ensure you're using the same browser.`);
      }
      
      // Generate real signature using identity's private key
      const signResult = await api.demoSignWithKey(algorithm, res.challenge, storedPrivateKey);
      setSignatureData(signResult);
      
      await new Promise(r => setTimeout(r, 300));
      
      setStep(2);
      const authResult = await api.authenticate({ did, signature: signResult.signature });
      setResult(authResult);
      // Navigate to verification result page
      navigate(`/app/verify/${did}/${authResult.verified ? 'success' : 'failure'}`);
    } catch (e) {
      setError(e.message || 'Authentication failed. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Authentication</h1>
        <p className="text-sm text-gray-400">Challenge-response authentication using decentralized identity</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <Card>
          <CardHeader title="Authenticate Identity" subtitle="Verify identity using cryptographic challenge-response" />
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">DID</label>
              <input
                type="text"
                className="input-field font-mono text-sm"
                placeholder="did:qidentity:..."
                value={did}
                onChange={(e) => setDid(e.target.value)}
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            <button
              onClick={handleRequestChallenge}
              disabled={loading || !did.trim()}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {steps[step]}
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4" />
                  Start Authentication
                </>
              )}
            </button>
          </div>
        </Card>

        <div className="space-y-4">
          {challenge && (
            <Card>
              <CardHeader title="Challenge" subtitle="Server-generated random challenge" />
              <div className="bg-navy-900/50 p-4 rounded-xl">
                <p className="text-xs font-mono text-gray-300 break-all">{challenge.challenge}</p>
              </div>
              <p className="text-xs text-gray-500 mt-3">Expires: {challenge.expires_at ? new Date(challenge.expires_at).toLocaleTimeString() : 'N/A'}</p>
            </Card>
          )}

          {signatureData && (
            <Card className="border-blue-500/20">
              <CardHeader title="Digital Signature Output" subtitle="Challenge signed with private key" />
              <div className="space-y-4">
                <div className="bg-navy-900/50 p-4 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs text-gray-400">Algorithm: {signatureData.algorithm}</p>
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">SIGNATURE</span>
                  </div>
                  <p className="text-xs font-mono text-white break-all bg-navy-900 p-3 rounded">{signatureData.signature}</p>
                  <div className="flex gap-2 mt-2">
                    <button onClick={() => copyToClipboard(signatureData.signature, 'Signature')} className="btn-outline text-xs flex items-center gap-1">
                      <Copy className="w-3 h-3" /> Copy
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="bg-navy-800/50 p-4 rounded-xl">
                    <p className="text-xs text-gray-500">Signature Size</p>
                    <p className="text-2xl font-bold text-blue-400">{signatureData.signature_size_bytes} bytes</p>
                  </div>
                  <div className="bg-navy-800/50 p-4 rounded-xl">
                    <p className="text-xs text-gray-500">Security Level</p>
                    <p className="text-2xl font-bold text-blue-400">{signatureData.security_level}</p>
                  </div>
                </div>
                
                <div className="bg-navy-800/50 p-4 rounded-xl">
                  <p className="text-xs text-gray-500 mb-2">Message Signed (Challenge)</p>
                  <p className="text-xs font-mono text-gray-300 break-all">{signatureData.message}</p>
                </div>
              </div>
            </Card>
          )}

          {result && (
            <Card className={result.verified ? 'border-emerald-500/20' : 'border-red-500/20'}>
              <div className="flex items-center gap-3 mb-4">
                {result.verified ? (
                  <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                ) : (
                  <XCircle className="w-8 h-8 text-red-400" />
                )}
                <div>
                  <h3 className={`text-lg font-bold ${result.verified ? 'text-emerald-400' : 'text-red-400'}`}>
                    {result.verified ? 'IDENTITY VERIFIED ✓' : 'AUTHENTICATION FAILED ✗'}
                  </h3>
                  <p className="text-sm text-gray-400">{result.message}</p>
                </div>
              </div>

              <div className="space-y-2 mt-4">
                {[
                  ['Signature', result.verified ? 'Valid' : 'Invalid'],
                  ['Identity Status', result.identity_status],
                  ['Algorithm', result.algorithm],
                  ['Blockchain', result.blockchain_verified ? 'Verified' : 'Not on chain'],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between py-1.5 border-b border-white/5">
                    <span className="text-sm text-gray-400">{k}</span>
                    <span className={`text-sm font-medium ${(v === 'Valid' || v === 'Verified') ? 'text-emerald-400' : v === 'Invalid' ? 'text-red-400' : 'text-white'}`}>{v}</span>
                  </div>
                ))}
                
                {signatureData && (
                  <div className="pt-4 border-t border-white/5">
                    <p className="text-xs text-gray-500 mb-2">Verification Details</p>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="bg-navy-900/50 p-3 rounded">
                        <p className="text-gray-400">Public Key Used</p>
                        <p className="font-mono text-white break-all">{signatureData.public_key}</p>
                      </div>
                      <div className="bg-navy-900/50 p-3 rounded">
                        <p className="text-gray-400">Signature Verified</p>
                        <p className="font-mono text-white break-all">{signatureData.signature}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

          {!challenge && !result && (
            <Card>
              <CardHeader title="Authentication Flow" />
              <div className="space-y-3">
                {[
                  'User requests authentication',
                  'Server generates random challenge',
                  'User signs challenge with private key',
                  'Signature sent to server',
                  'Server verifies signature with public key',
                  'Blockchain identity status checked',
                  'Authentication result returned',
                ].map((step, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-navy-700 rounded-full flex items-center justify-center shrink-0">
                      <span className="text-[10px] font-bold text-gray-400">{i + 1}</span>
                    </div>
                    <p className="text-sm text-gray-400">{step}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
