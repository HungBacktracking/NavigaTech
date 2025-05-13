import { Navigate, Route, Routes } from 'react-router-dom';
import AuthLayout from '../pages/auth/layout';
import MainLayout from '../pages/layout';
import { lazy } from 'react';
import AuthGuard from '../components/auth/auth-guard';

const JobFinderPage = lazy(() => import('../pages/job-finder'));
const JobAnalysisPage = lazy(() => import('../pages/job-analysis'));
const AIAssistantPage = lazy(() => import('../pages/ai-assistant'));
const AuthPage = lazy(() => import('../pages/auth/index'));
const UploadCVPage = lazy(() => import('../pages/auth/upload-cv'));
const NotFoundPage = lazy(() => import('../pages/interrupts/not-found-page'));
const MyProfilePage = lazy(() => import('../pages/profile'));

const AppRouter = () => {
  return (
    <Routes>
      <Route path="auth/*" element={<AuthLayout />}>
        <Route index element={<AuthPage />} />
      </Route>

      <Route path="/" element={<AuthGuard />}>
        <Route element={<MainLayout />}>
          <Route index element={<Navigate to="/home" replace />} />
          <Route path="home" element={<JobFinderPage />} />
          <Route path="job-analysis" element={<JobAnalysisPage />} />
          <Route path="ai-assistant">
            <Route index element={<AIAssistantPage />} />
            <Route path=":conversationId" element={<AIAssistantPage />} />
          </Route>
          <Route path="my-profile" element={<MyProfilePage />} />
          <Route path="upload-cv" element={<UploadCVPage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRouter;