import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/auth/auth-context';
import FullscreenLoader from '../fullscreen-loader';

const AuthGuard = () => {
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/auth';
    }
  }, [isAuthenticated]);

  return isLoading || !isAuthenticated ? (
    <FullscreenLoader />
  ) : (
    <Outlet />
  );
};

export default AuthGuard;
