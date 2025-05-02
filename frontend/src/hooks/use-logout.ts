import { useAuth } from '../contexts/auth/auth-context';
import { removeTokens } from '../lib/helpers/auth-tokens';

export const useLogout = () => {
  const { reset } = useAuth();

  const logout = () => {
    reset();
    removeTokens();
    window.location.href = '/auth';
  };

  return { logout };
};
