const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  // Users
  createUser: (data) => request('/users', { method: 'POST', body: JSON.stringify(data) }),
  getUser: (id) => request(`/users/${id}`),

  // Identity
  createIdentity: (data) => request('/identity/create', { method: 'POST', body: JSON.stringify(data) }),
  getIdentity: (did) => request(`/identity/${did}`),
  listIdentities: (userId) => request(`/identities${userId ? `?user_id=${userId}` : ''}`),

  // Auth
  getChallenge: (did) => request(`/identity/authenticate/challenge?did=${did}`, { method: 'POST' }),
  authenticate: (data) => request('/identity/authenticate', { method: 'POST', body: JSON.stringify(data) }),

  // Migration
  migrate: (data) => request('/identity/migrate', { method: 'POST', body: JSON.stringify(data) }),
  getMigrationHistory: (did) => request(`/identity/${did}/migration-history`),

  // Revocation
  revoke: (data) => request('/identity/revoke', { method: 'POST', body: JSON.stringify(data) }),

  // Tamper check
  tamperCheck: (did, name) => request(`/identity/${did}/tamper-check${name ? `?modified_name=${name}` : ''}`, { method: 'POST' }),

  // Quantum
  getQuantumReadiness: (algo) => request(`/quantum/readiness/${algo}`),
  getAllAssessments: () => request('/quantum/readiness-all'),

  // Blockchain
  getBlockchainTransactions: (did) => request(`/blockchain/transactions${did ? `?did=${did}` : ''}`),
  getBlockchainStatus: () => request('/blockchain/status'),

  // Benchmarks
  runBenchmark: (data) => request('/benchmark/run', { method: 'POST', body: JSON.stringify(data) }),
  getBenchmarkHistory: (algo) => request(`/benchmark/history${algo ? `?algorithm=${algo}` : ''}`),

  // Research
  getResearchSummary: () => request('/research/summary'),

  // Demo
  getAlgorithms: () => request('/demo/algorithms'),
  demoKeygen: (algorithm) => request('/demo/keygen', { method: 'POST', body: JSON.stringify({ algorithm }) }),
  demoSign: (algorithm, message) => request('/demo/sign', { method: 'POST', body: JSON.stringify({ algorithm, message }) }),
  demoSignWithKey: (algorithm, message, privateKey) => request('/demo/sign-with-key', { method: 'POST', body: JSON.stringify({ algorithm, message, private_key: privateKey }) }),
  demoVerify: (algorithm, message, signature, publicKey, privateKey) => request('/demo/verify', { method: 'POST', body: JSON.stringify({ algorithm, message, signature, public_key: publicKey, private_key: privateKey }) }),
};
