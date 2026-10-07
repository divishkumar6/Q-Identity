import clsx from 'clsx';

export function StatusBadge({ status }) {
  const styles = {
    active: 'badge-green',
    confirmed: 'badge-green',
    completed: 'badge-green',
    migrated: 'badge-blue',
    revoked: 'badge-red',
    failed: 'badge-red',
    pending: 'badge-gold',
  };
  return (
    <span className={clsx(styles[status] || 'badge-gold', 'capitalize')}>
      {status}
    </span>
  );
}

export function AlgorithmBadge({ algorithm }) {
  const styles = {
    ECDSA: 'badge-gold',
    HYBRID: 'badge-blue',
    'ML-DSA': 'badge-green',
  };
  return (
    <span className={clsx(styles[algorithm] || 'badge-gold')}>
      {algorithm}
    </span>
  );
}

export function LoadingSpinner({ text = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center gap-3 py-12">
      <div className="w-5 h-5 border-2 border-gold-500/30 border-t-gold-500 rounded-full animate-spin" />
      <span className="text-gray-400 text-sm">{text}</span>
    </div>
  );
}

export function ErrorDisplay({ message }) {
  return (
    <div className="glass-card p-6 border-red-500/20">
      <p className="text-red-400 text-sm">{message}</p>
    </div>
  );
}

export function EmptyState({ icon, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="text-gray-600 mb-4">{icon}</div>}
      <h3 className="text-lg font-semibold text-gray-300 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 max-w-sm">{description}</p>
    </div>
  );
}

export function Card({ children, className, ...props }) {
  return (
    <div className={clsx('glass-card p-6', className)} {...props}>
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, action }) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
