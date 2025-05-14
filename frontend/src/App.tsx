import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import AppRouter from './routes';
import { Suspense } from 'react';
import queryClient from './lib/clients/query-client';
import AuthProvider from './contexts/auth/auth-provider';
import FullscreenLoader from './components/fullscreen-loader';
import NotificationsProvider from './components/notifications';
import './App.css';

function App() {
  return (
    <Suspense fallback={<FullscreenLoader />}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <NotificationsProvider>
            <AppRouter />
          </NotificationsProvider>
        </AuthProvider>
        {/* <ReactQueryDevtools initialIsOpen={false} /> */}
      </QueryClientProvider>
    </Suspense>
  );
}

export default App;
