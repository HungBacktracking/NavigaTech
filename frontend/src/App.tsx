import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import './App.css';
import { Spin } from 'antd';
import AppRouter from './routes';
import { Suspense } from 'react';
import queryClient from './lib/clients/query-client';
import AuthProvider from './contexts/auth/auth-provider';

function App() {
  return (
    <Suspense
      fallback={
        <Spin
          size="large"
          tip="Loading..."
          style={{
            width: '100%',
            height: '100vh',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        />
      }
    >
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AppRouter />
        </AuthProvider>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </Suspense>
  );
}

export default App;
