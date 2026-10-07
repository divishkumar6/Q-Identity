import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import DashboardLayout from './layouts/DashboardLayout'
import OverviewPage from './pages/OverviewPage'
import CreateIdentityPage from './pages/CreateIdentityPage'
import MyIdentitiesPage from './pages/MyIdentitiesPage'
import IdentityDetailPage from './pages/IdentityDetailPage'
import AuthenticationPage from './pages/AuthenticationPage'
import VerificationResultPage from './pages/VerificationResultPage'
import QuantumReadinessPage from './pages/QuantumReadinessPage'
import MigrationPage from './pages/MigrationPage'
import BlockchainExplorerPage from './pages/BlockchainExplorerPage'
import BenchmarksPage from './pages/BenchmarksPage'
import ResearchPage from './pages/ResearchPage'
import SimulationPage from './pages/SimulationPage'
import LandingPage from './pages/LandingPage'

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app" element={<DashboardLayout />}>
            <Route index element={<OverviewPage />} />
            <Route path="create" element={<CreateIdentityPage />} />
            <Route path="identities" element={<MyIdentitiesPage />} />
            <Route path="identity/:did" element={<IdentityDetailPage />} />
            <Route path="authenticate" element={<AuthenticationPage />} />
            <Route path="verify/:did/:verified" element={<VerificationResultPage />} />
            <Route path="quantum" element={<QuantumReadinessPage />} />
            <Route path="migration" element={<MigrationPage />} />
            <Route path="blockchain" element={<BlockchainExplorerPage />} />
            <Route path="benchmarks" element={<BenchmarksPage />} />
            <Route path="research" element={<ResearchPage />} />
            <Route path="simulation" element={<SimulationPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
