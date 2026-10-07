import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, Search, ExternalLink } from 'lucide-react';
import { api } from '../services/api';
import { Card, LoadingSpinner, EmptyState, StatusBadge, AlgorithmBadge } from '../components/shared';

export default function MyIdentitiesPage() {
  const [identities, setIdentities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    api.listIdentities()
      .then((data) => setIdentities(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load identities. Make sure the backend is running.'))
      .finally(() => setLoading(false));
  }, []);

  const filtered = (identities || []).filter(
    (id) => id.did?.includes(search) || id.algorithm?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <LoadingSpinner text="Loading identities..." />;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">My Identities</h1>
        <p className="text-sm text-gray-400">Manage your decentralized identities</p>
      </div>

      {error && (
        <Card className="mb-6 border-red-500/20">
          <p className="text-sm text-red-400">{error}</p>
        </Card>
      )}

      <div className="mb-6 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          className="input-field pl-10"
          placeholder="Search by DID or algorithm..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={<Users className="w-12 h-12" />}
          title="No Identities Found"
          description="Create your first decentralized identity to get started."
        />
      ) : (
        <div className="space-y-3">
          {filtered.map((id) => (
            <Link key={id.did} to={`/app/identity/${id.did}`}>
              <Card className="hover:border-gold-500/20 transition-all cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gold-500/10 rounded-xl flex items-center justify-center">
                      <span className="text-sm font-bold text-gold-400">
                        {id.algorithm === 'ECDSA' ? 'E' : id.algorithm === 'HYBRID' ? 'H' : 'M'}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-mono text-white">{id.did}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <AlgorithmBadge algorithm={id.algorithm} />
                        <StatusBadge status={id.status} />
                      </div>
                    </div>
                  </div>
                  <ExternalLink className="w-4 h-4 text-gray-500" />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
