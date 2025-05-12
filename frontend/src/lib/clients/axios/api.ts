import axios, { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import { APP_CONFIG } from '../../app-config';
import { getToken, removeTokens } from '../../helpers/auth-tokens';
import queryClient from '../query-client';
import { HttpStatusCode } from 'axios';

interface CustomInternalAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

// let isRefreshing = false;
// let failedQueue: { resolve: (value: unknown) => void; reject: (reason?: any) => void }[] = [];

const api = axios.create({
  baseURL: APP_CONFIG.API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const requestAuthInterceptor = (config: AxiosRequestConfig) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config as InternalAxiosRequestConfig;
};

// const processQueue = (error: AxiosError | null, token: string | null = null) => {
//   failedQueue.forEach((prom) => {
//     if (error) {
//       prom.reject(error);
//     } else {
//       prom.resolve(token);
//     }
//   });
//   failedQueue = [];
// };

const handleTokenExpiration = () => {
  removeTokens();
  queryClient.invalidateQueries();
  window.location.href = '/auth';
};

const responseAuthInterceptor = (response: any) => response;

const responseAuthErrorInterceptor = async (error: AxiosError) => {
  if (!error.response || !error.config) {
    return Promise.reject(error);
  }

  const originalRequest = error.config as CustomInternalAxiosRequestConfig;

  if (error.response.status === HttpStatusCode.Unauthorized && !originalRequest._retry) {
      // Since we don't have a refresh token endpoint, just logout the user
      handleTokenExpiration();
      return Promise.reject(error);
    }

  return Promise.reject(error);
};

api.interceptors.request.use(requestAuthInterceptor);
api.interceptors.response.use(responseAuthInterceptor, responseAuthErrorInterceptor);

export default api;
