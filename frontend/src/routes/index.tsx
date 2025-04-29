import { Navigate, Route, Routes } from 'react-router-dom';
import AuthLayout from '../pages/auth/layout';
import MainLayout from '../pages/layout';
import { lazy } from 'react';


const JobFinderPage = lazy(() => import('../pages/job-finder'));
const JobAnalysisPage = lazy(() => import('../pages/job-analysis'));
const AIAssistantPage = lazy(() => import('../pages/ai-assistant'));


const AppRouter = () => {
  return (
    <Routes>
      <Route path="auth/*" element={<AuthLayout />}>
        <Route path="login" element={<div>Login Page</div>} />
        <Route path="register" element={<div>Register Page</div>} />
      </Route>

      <Route path="/*" element={<MainLayout />}>
        <Route index element={<Navigate to="/home" replace />} />
        <Route path="home" element={<JobFinderPage />} />
        <Route path="job-analysis" element={<JobAnalysisPage />} />
        <Route path="ai-assistant" element={<AIAssistantPage />} />
      </Route>

      <Route path="*" element={<div>Not found page</div>} />
    </Routes>
  );
};

export default AppRouter;