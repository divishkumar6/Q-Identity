import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, UserPlus, Users, Shield, Brain, ArrowRightLeft,
  Link2, BarChart3, FlaskConical, Atom, ChevronRight, Lock
} from 'lucide-react';

const navItems = [
  { to: '/app', icon: LayoutDashboard, label: 'Overview', end: true },
  { divider: 'Identity' },
  { to: '/app/create', icon: UserPlus, label: 'Create Identity' },
  { to: '/app/identities', icon: Users, label: 'My Identities' },
  { divider: 'Security' },
  { to: '/app/authenticate', icon: Shield, label: 'Authentication' },
  { to: '/app/quantum', icon: Brain, label: 'Quantum Readiness' },
  { to: '/app/migration', icon: ArrowRightLeft, label: 'PQC Migration' },
  { divider: 'Blockchain & Research' },
  { to: '/app/blockchain', icon: Link2, label: 'Blockchain Explorer' },
  { to: '/app/benchmarks', icon: BarChart3, label: 'Benchmarks' },
  { to: '/app/research', icon: FlaskConical, label: 'Research' },
  { to: '/app/simulation', icon: Atom, label: 'Simulation' },
];

export default function DashboardLayout() {
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-navy-900/80 border-r border-white/5 flex flex-col shrink-0">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gold-500/15 rounded-xl flex items-center justify-center">
              <Lock className="w-4.5 h-4.5 text-gold-400" />
            </div>
            <div>
              <h1 className="text-base font-display font-bold text-white tracking-tight">Q-Identity</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest">Quantum-Ready</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3">
          {navItems.map((item, i) => {
            if (item.divider) {
              return (
                <div key={i} className="mt-5 mb-2 px-3">
                  <span className="text-[10px] font-semibold uppercase tracking-widest text-gray-600">
                    {item.divider}
                  </span>
                </div>
              );
            }
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 mb-0.5 ${
                    isActive
                      ? 'bg-gold-500/10 text-gold-400 border border-gold-500/20'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-transparent'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-white/5">
          <p className="text-[10px] text-gray-600">Q-Identity v1.0.0</p>
          <p className="text-[10px] text-gray-600">Post-Quantum Research Platform</p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
