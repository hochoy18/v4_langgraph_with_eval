import { Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import ResearchPage from './pages/ResearchPage';
import ReportPage from './pages/ReportPage';
import HistoryPage from './pages/HistoryPage';
import EvalPage from './pages/EvalPage';

/**
 * Phase 0 仅占位 — 各页面后续 Phase 填充。
 */
export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Routes>
        <Route path="/" element={<Navigate to="/research" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/research" element={<ResearchPage />} />
        <Route path="/research/:jobId" element={<ResearchPage />} />
        <Route path="/reports/:reportId" element={<ReportPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/eval" element={<EvalPage />} />
        <Route path="*" element={<Navigate to="/research" replace />} />
      </Routes>
    </div>
  );
}