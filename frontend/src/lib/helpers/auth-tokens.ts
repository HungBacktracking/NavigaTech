import { AuthKey } from "../constants/auth-key";


export const setToken = (token: string) => {
  localStorage.setItem(AuthKey.TOKEN, token);
};

export const getToken = () => {
  return localStorage.getItem(AuthKey.TOKEN);
};

export const removeToken = () => {
  localStorage.removeItem(AuthKey.TOKEN);
};

export const setRefreshToken = (token: string) => {
  localStorage.setItem(AuthKey.REFRESH_TOKEN, token);
};

export const getRefreshToken = () => {
  return localStorage.getItem(AuthKey.REFRESH_TOKEN);
};

export const removeRefreshToken = () => {
  localStorage.removeItem(AuthKey.REFRESH_TOKEN);
};

export const removeTokens = () => {
  removeToken();
  removeRefreshToken();
};
