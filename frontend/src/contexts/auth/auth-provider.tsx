import { ReactNode } from 'react';
import { AuthContext, useAuthProvider } from './auth-context';

interface IProps {
  children: ReactNode;
}

const AuthProvider = (props: IProps) => {
  const { children } = props;

  const auth = useAuthProvider();
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
