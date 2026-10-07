import { Link } from 'react-router-dom';
import { Lock, ChevronRight, Shield, Brain, Link2, Zap } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-navy-950">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 bg-navy-950/80 backdrop-blur-lg border-b border-white/5">
        <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gold-500/15 rounded-lg flex items-center justify-center">
              <Lock className="w-4 h-4 text-gold-400" />
            </div>
            <span className="font-display font-bold text-white">Q-Identity</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/app" className="btn-secondary text-sm">Dashboard</Link>
            <Link to="/app" className="btn-primary text-sm">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gold-500/10 border border-gold-500/20 rounded-full mb-8">
            <div className="w-2 h-2 bg-gold-400 rounded-full animate-pulse" />
            <span className="text-xs font-medium text-gold-400">Post-Quantum Research Platform</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-display font-bold text-white leading-tight mb-6">
            Quantum-Ready
            <br />
            <span className="text-gold-400">Decentralized Identity</span>
          </h1>

          <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Preparing blockchain identity systems for the post-quantum era.
            Evaluate cryptographic readiness, migrate identity keys, and measure the
            practical impact of post-quantum cryptography on blockchain-based identity systems.
          </p>

          <div className="flex items-center justify-center gap-4">
            <Link to="/app" className="btn-primary text-base px-8 py-3 flex items-center gap-2">
              Explore Platform <ChevronRight className="w-4 h-4" />
            </Link>
            <Link to="/app" className="btn-outline text-base px-8 py-3">
              Run Demonstration
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-8 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Shield, title: 'Crypto-Agility Layer', desc: 'Seamlessly switch between ECDSA, Hybrid, and ML-DSA cryptography without changing the identity workflow.' },
              { icon: Brain, title: 'Quantum Readiness Analysis', desc: 'Assess the quantum vulnerability of your current cryptographic configuration with transparent scoring.' },
              { icon: Link2, title: 'Blockchain-Backed Identity', desc: 'DIDs and cryptographic state recorded on-chain with full transaction history and migration tracking.' },
            ].map((f, i) => (
              <div key={i} className="glass-card p-8 hover:border-gold-500/20 transition-all duration-300">
                <div className="w-12 h-12 bg-gold-500/10 rounded-2xl flex items-center justify-center mb-5">
                  <f.icon className="w-5 h-5 text-gold-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">{f.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="py-12 px-8 border-t border-white/5">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-xs text-gray-500 leading-relaxed">
            This project demonstrates how blockchain-based decentralized identity can prepare for the
            future quantum threat by integrating standardized post-quantum cryptography through a
            crypto-agile architecture and measuring the practical cost of that transition. Current
            quantum computers cannot practically break production-strength blockchain cryptography.
          </p>
        </div>
      </section>
    </div>
  );
}
