import { IAuthLoginResponse } from "../lib/types/auth";
import { IUser, UserLoginDto } from "../lib/types/user";

export const authApi = {
  login: async (userCrendentials: UserLoginDto) : Promise<IAuthLoginResponse> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          access_token: "mock_access_token",
          refresh_token: "mock_refresh_token",
          user: {
            email: userCrendentials.email,
            cvUploaded: true
          },
        });
      }, 100);
    });
  },

  register: async (userData: UserLoginDto): Promise<IUser> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          email: userData.email,
          cvUploaded: false
        });
      }, 100);
    });
  },

  getCurrentUser: async (): Promise<IUser> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          email: "mock_email@gmail.com",
          cvUploaded: localStorage.getItem("cv_uploaded") === "true"
        });
      }, 100);
    });
  },
  
  uploadCV: async (file: File): Promise<boolean> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        localStorage.setItem("cv_uploaded", "true");
        resolve(true);
      }, 4000);
    });
  }
};