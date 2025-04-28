import axios, { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import { APP_CONFIG } from '../../app-config';
import { getToken, setToken, removeTokens, getRefreshToken } from '../../helpers/auth-tokens';
import queryClient from '../query-client';
import { HttpStatusCode } from 'axios';

interface CustomInternalAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

let isRefreshing = false;
let failedQueue: { resolve: (value: unknown) => void; reject: (reason?: any) => void }[] = [];

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

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

const refreshAuthToken = async (refreshToken: string): Promise<string> => {
  try {
    const response = await axios.post(`${APP_CONFIG.API_URL}/auth/refresh`, {
      refreshToken
    });
    
    const newAccessToken = response.data.access_token;
    setToken(newAccessToken);
    return newAccessToken;
  } catch (error) {
    throw error;
  }
};

const handleLogout = () => {
  removeTokens();
  queryClient.invalidateQueries();
  isRefreshing = false;
  window.location.href = '/auth';
};

const responseAuthInterceptor = (response: any) => response;

const responseAuthErrorInterceptor = async (error: AxiosError) => {
  if (!error.response || !error.config) {
    return Promise.reject(error);
  }

  const originalRequest = error.config as CustomInternalAxiosRequestConfig;

  if (error.response.status === HttpStatusCode.Unauthorized && !originalRequest._retry) {
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = getRefreshToken();
    
    if (!refreshToken) {
      handleLogout();
      return Promise.reject(error);
    }

    try {
      const newAccessToken = await refreshAuthToken(refreshToken);
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      processQueue(null, newAccessToken);
      isRefreshing = false;
      
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(error, null);
      handleLogout();
      return Promise.reject(refreshError);
    }
  }

  return Promise.reject(error);
};

api.interceptors.request.use(requestAuthInterceptor);
api.interceptors.response.use(responseAuthInterceptor, responseAuthErrorInterceptor);

export default api;