import { useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/auth/auth-context';
import FullscreenLoader from '../fullscreen-loader';

const AuthGuard = () => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated || !user) {
        navigate('/auth', { replace: true });
      } else if (user && !user.uploaded_resume && location.pathname !== '/upload-cv') {
        navigate('/auth/upload-cv', { replace: true });
      }
    }
  }, [isAuthenticated, isLoading, user, navigate, location.pathname]);

  if (isLoading) {
    return <FullscreenLoader />;
  }

  return isAuthenticated ? <Outlet /> : <FullscreenLoader />;
};

export default AuthGuard;
