import { createContext, useContext, useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { User } from '../../lib/types/user';
import { getToken } from '../../lib/helpers/auth-tokens';
import { authApi } from '../../services/auth';

export interface IAuthContext {
  isAuthenticated: boolean;
  user?: User;
  reset: () => void;
  isLoading: boolean;
}

export const AuthContext = createContext<IAuthContext | undefined>(undefined);

export const useAuthProvider = (): IAuthContext => {
  const [user, setUser] = useState<User>();
  const isAuthenticatedBefore = !!getToken();
  const [isAuthenticated, setIsAuthenticated] = useState(isAuthenticatedBefore);

  const { isLoading, data } = useQuery<User, Error>({
    queryKey: ['auth/current-user'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticatedBefore,
  });

  useEffect(() => {
    if (data) {
      setUser(data);
      setIsAuthenticated(true);
    }
  }, [data]);

  const reset = () => {
    setUser(undefined);
    setIsAuthenticated(false);
  };

  return { isAuthenticated, user, reset, isLoading };
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within a provider');
  }
  return context;
};
