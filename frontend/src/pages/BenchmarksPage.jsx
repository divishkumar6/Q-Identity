import { useState } from 'react';
import { BarChart3, Loader2, Play } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { api } from '../services/api';
import { Card, CardHeader } from '../components/shared';

export default function BenchmarksPage() {
  const [iterations, setIterations] = useState(100);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const runBenchmark = async () => {
    setRunning(true);
    setError(null);
    setResults([]);
    try {
      const data = await api.runBenchmark({ iterations, operations: ['keygen', 'sign', 'verify'] });
      setResults(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e.message || 'Benchmark failed');
    } finally {
      setRunning(false);
    }
  };

  const grouped = {};
  results.forEach((r) => {
    if (!grouped[r.operation]) grouped[r.operation] = [];
    grouped[r.operation].push(r);
  });

  const chartData = Object.entries(grouped).map(([op, data]) => ({
    operation: op === 'keygen' ? 'Key Generation' : op === 'sign' ? 'Signing' : 'Verification',
    ECDSA: data.find((d) => d.algorithm === 'ECDSA')?.avg_time_ms || 0,
    HYBRID: data.find((d) => d.algorithm === 'HYBRID')?.avg_time_ms || 0,
    'ML-DSA': data.find((d) => d.algorithm === 'ML-DSA')?.avg_time_ms || 0,
  }));

  const sizeData = results
    .filter((r) => r.avg_signature_size || r.avg_key_size)
    .reduce((acc, r) => {
      const existing = acc.find((a) => a.algorithm === r.algorithm);
      if (!existing) {
        acc.push({
          algorithm: r.algorithm,
          signatureSize: r.avg_signature_size || 0,
          keySize: r.avg_key_size || 0,
        });
      }
      return acc;
    }, []);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white mb-2">Cryptographic Benchmarks</h1>
        <p className="text-sm text-gray-400">Measure and compare performance of ECDSA, Hybrid, and ML-DSA</p>
      </div>

      <Card className="mb-8">
        <div className="flex items-end gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-2">Iterations</label>
            <select
              className="input-field"
              value={iterations}
              onChange={(e) => setIterations(Number(e.target.value))}
            >
              {[10, 50, 100, 500, 1000].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
          <button
            onClick={runBenchmark}
            disabled={running}
            className="btn-primary flex items-center gap-2"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {running ? 'Running...' : 'Run Benchmark'}
          </button>
        </div>
        {running && (
          <div className="mt-4 flex items-center gap-3">
            <div className="w-4 h-4 border-2 border-gold-500/30 border-t-gold-500 rounded-full animate-spin" />
            <span className="text-sm text-gray-400">Running {iterations} iterations for each algorithm...</span>
          </div>
        )}
      </Card>

      {error && (
        <Card className="mb-8 border-red-500/20">
          <p className="text-sm text-red-400">{error}</p>
        </Card>
      )}

      {results.length > 0 && (
        <>
          <Card className="mb-8">
            <CardHeader title="Benchmark Results" subtitle={`${iterations} iterations per algorithm`} />
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="text-left py-3 text-gray-500 font-medium">Algorithm</th>
                    <th className="text-left py-3 text-gray-500 font-medium">Operation</th>
                    <th className="text-right py-3 text-gray-500 font-medium">Avg (ms)</th>
                    <th className="text-right py-3 text-gray-500 font-medium">Min (ms)</th>
                    <th className="text-right py-3 text-gray-500 font-medium">Max (ms)</th>
                    <th className="text-right py-3 text-gray-500 font-medium">Median</th>
                    <th className="text-right py-3 text-gray-500 font-medium">Std Dev</th>
                    <th className="text-right py-3 text-gray-500 font-medium">Sig Size</th>
                    <th className="text-right py-3 text-gray-500 font-medium">Key Size</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, i) => (
                    <tr key={i} className="border-b border-white/3">
                      <td className="py-3 text-white font-medium">{r.algorithm}</td>
                      <td className="py-3 text-gray-300">{r.operation}</td>
                      <td className="py-3 text-right text-white">{r.avg_time_ms?.toFixed(4)}</td>
                      <td className="py-3 text-right text-gray-400">{r.min_time_ms?.toFixed(4)}</td>
                      <td className="py-3 text-right text-gray-400">{r.max_time_ms?.toFixed(4)}</td>
                      <td className="py-3 text-right text-gray-400">{r.median_time_ms?.toFixed(4)}</td>
                      <td className="py-3 text-right text-gray-400">{r.std_dev_ms?.toFixed(4)}</td>
                      <td className="py-3 text-right text-gray-400">{r.avg_signature_size || '—'}</td>
                      <td className="py-3 text-right text-gray-400">{r.avg_key_size || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <div className="grid lg:grid-cols-2 gap-6 mb-8">
            <Card>
              <CardHeader title="Performance Comparison" subtitle="Average time per operation (ms)" />
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="operation" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#151d38', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12 }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Legend />
                  <Bar dataKey="ECDSA" fill="#e5ab3d" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="HYBRID" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="ML-DSA" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card>
              <CardHeader title="Signature & Key Sizes" subtitle="Average sizes in bytes" />
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={sizeData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="algorithm" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#151d38', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12 }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Legend />
                  <Bar dataKey="signatureSize" name="Signature Size" fill="#e5ab3d" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="keySize" name="Key Size" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </>
      )}

      {results.length === 0 && !running && !error && (
        <Card>
          <div className="text-center py-12">
            <BarChart3 className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">Run a benchmark to see results</p>
            <p className="text-xs text-gray-500 mt-2">Results are based on real measurements with multiple iterations</p>
          </div>
        </Card>
      )}
    </div>
  );
}
