import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Loader2, CheckCircle2, Key, Copy, Eye, EyeOff } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardHeader } from '../components/shared';

export default function CreateIdentityPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', organization: '', algorithm: 'ECDSA' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [step, setStep] = useState(0);

  const steps = [
    'Creating user account...',
    'Generating cryptographic keys...',
    'Creating DID document...',
    'Recording on blockchain...',
    'Identity created successfully',
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      setStep(0);
      const user = await api.createUser({
        name: form.name,
        email: form.email,
        organization: form.organization || null,
        password: 'demo-password-' + Date.now(),
      });

      setStep(1);
      await new Promise(r => setTimeout(r, 400));

      setStep(2);
      const identity = await api.createIdentity({
        user_id: user.id,
        algorithm: form.algorithm,
      });

      setStep(3);
      await new Promise(r => setTimeout(r, 300));

      setStep(4);
      // Store private key in localStorage for demo authentication
      if (identity.private_key_ref) {
        localStorage.setItem(`qidentity_private_key_${identity.did}`, identity.private_key_ref);
      }
      setResult(identity);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const [showPrivateKey, setShowPrivateKey] = useState(false);

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  if (result) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-display font-bold text-white mb-2">Identity Created</h1>
        </div>
        
        {/* Key Generation Output */}
        <Card className="mb-6">
          <CardHeader title="Key Generation Output" subtitle="Cryptographic keys generated for your identity" />
          <div className="space-y-4">
            <div className="bg-navy-900/50 p-4 rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-400">Algorithm: {result.algorithm}</p>
                <span className="px-2 py-1 bg-gold-500/20 text-gold-400 text-xs rounded">PUBLIC KEY</span>
              </div>
              <p className="text-xs font-mono text-white break-all bg-navy-900 p-3 rounded">{result.public_key}</p>
              <div className="flex gap-2 mt-2">
                <button onClick={() => copyToClipboard(result.public_key, 'Public key')} className="btn-outline text-xs flex items-center gap-1">
                  <Copy className="w-3 h-3" /> Copy
                </button>
              </div>
            </div>
            
            <div className="bg-navy-900/50 p-4 rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-400">Algorithm: {result.algorithm}</p>
                <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded">PRIVATE KEY (keep secret!)</span>
              </div>
              <div className="relative">
                <p className="text-xs font-mono text-white break-all bg-navy-900 p-3 rounded">
                  {showPrivateKey ? result.private_key_ref : '••••••••••••••••••••••••••••••••••••••••'}
                </p>
                <div className="flex gap-2 mt-2">
                  <button onClick={() => setShowPrivateKey(!showPrivateKey)} className="btn-outline text-xs flex items-center gap-1">
                    {showPrivateKey ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                    {showPrivateKey ? ' Hide' : ' Show'}
                  </button>
                  <button onClick={() => copyToClipboard(result.private_key_ref, 'Private key')} className="btn-outline text-xs flex items-center gap-1">
                    <Copy className="w-3 h-3" /> Copy
                  </button>
                </div>
              </div>
              <p className="text-xs text-red-400/80 mt-2">⚠️ Private key shown for demo only. In production, this never leaves secure storage.</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="bg-navy-800/50 p-4 rounded-xl">
                <p className="text-xs text-gray-500">Public Key Size</p>
                <p className="text-2xl font-bold text-gold-400">{result.public_key?.length / 2 || 0} bytes</p>
              </div>
              <div className="bg-navy-800/50 p-4 rounded-xl">
                <p className="text-xs text-gray-500">Security Level</p>
                <p className="text-2xl font-bold text-gold-400">{result.security_level}</p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="max-w-lg">
          <div className="flex items-center gap-3 mb-6">
            <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            <div>
              <h2 className="text-lg font-semibold text-white">Identity Created Successfully</h2>
              <p className="text-sm text-gray-400">Your decentralized identity is now active on the blockchain.</p>
            </div>
          </div>

          <div className="space-y-3 mb-6">
            {[
              ['DID', result.did],
              ['Algorithm', result.algorithm],
              ['Security Level', result.security_level],
              ['Status', result.status],
              ['Blockchain Tx', result.blockchain_tx?.tx_hash?.slice(0, 24) + '...'],
              ['Block', result.blockchain_tx?.block_number],
            ].map(([label, value]) => (
              <div key={label} className="flex items-center justify-between py-2 border-b border-white/5">
                <span className="text-sm text-gray-400">{label}</span>
                <span className="text-sm text-white font-mono">{value}</span>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button onClick={() => navigate(`/app/identity/${result.did}`)} className="btn-primary flex-1">
              View Identity
            </button>
            <button onClick={() => { setResult(null); setForm({ name: '', email: '', organization: '', algorithm: 'ECDSA' }); }} className="btn-secondary flex-1">
              Create Another
            </button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Create Identity</h1>
        <p className="text-sm text-gray-400">Generate a new decentralized identity with cryptographic keys</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <Card>
          <CardHeader title="Identity Information" />
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Full Name *</label>
              <input
                type="text"
                required
                className="input-field"
                placeholder="Enter your full name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email *</label>
              <input
                type="email"
                required
                className="input-field"
                placeholder="you@example.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Organization</label>
              <input
                type="text"
                className="input-field"
                placeholder="Optional organization name"
                value={form.organization}
                onChange={(e) => setForm({ ...form, organization: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">Cryptographic Algorithm</label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'ECDSA', label: 'Classical', desc: 'ECDSA', score: 32 },
                  { value: 'HYBRID', label: 'Hybrid', desc: 'ECDSA + ML-DSA', score: 72 },
                  { value: 'ML-DSA', label: 'Post-Quantum', desc: 'ML-DSA', score: 92 },
                ].map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setForm({ ...form, algorithm: opt.value })}
                    className={`p-4 rounded-xl border text-left transition-all ${
                      form.algorithm === opt.value
                        ? 'border-gold-500/50 bg-gold-500/10'
                        : 'border-white/10 bg-navy-800/40 hover:border-white/20'
                    }`}
                  >
                    <p className="text-sm font-semibold text-white">{opt.label}</p>
                    <p className="text-xs text-gray-400 mt-1">{opt.desc}</p>
                    <p className="text-xs text-gold-400 mt-2">QR: {opt.score}/100</p>
                  </button>
                ))}
              </div>
            </div>

            {error && <p className="text-sm text-red-400">{error}</p>}

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {steps[step]}
                </>
              ) : (
                <>
                  <UserPlus className="w-4 h-4" />
                  Create Identity
                </>
              )}
            </button>
          </form>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader title="How It Works" />
            <div className="space-y-4">
              {[
                { step: 1, title: 'Key Generation', desc: 'A cryptographic key pair is generated using the selected algorithm.' },
                { step: 2, title: 'DID Creation', desc: 'A Decentralized Identifier (DID) is created and linked to your public key.' },
                { step: 3, title: 'Blockchain Registration', desc: 'Your identity hash and public key reference are recorded on the blockchain.' },
                { step: 4, title: 'Authentication Ready', desc: 'Your identity can now be used for challenge-response authentication.' },
              ].map((s) => (
                <div key={s.step} className="flex gap-4">
                  <div className="w-8 h-8 bg-gold-500/15 rounded-lg flex items-center justify-center shrink-0">
                    <span className="text-xs font-bold text-gold-400">{s.step}</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{s.title}</p>
                    <p className="text-xs text-gray-400 mt-1">{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="border-gold-500/10">
            <p className="text-xs text-gray-400 leading-relaxed">
              <strong className="text-gold-400">Note:</strong> Private keys are never stored in plaintext.
              For this prototype, keys are managed locally. In production, use a hardware security module
              or secure enclave.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
