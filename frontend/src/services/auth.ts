import { IAuthLoginResponse } from "../lib/types/auth";
import { User, UserDetail, UserLoginDto } from "../lib/types/user";
import { mockUserDetail } from "./user";

export interface UploadCVResponse {
  object_key: string;
  upload_url: string;
}

export const authApi = {
  login: async (userCrendentials: UserLoginDto) : Promise<IAuthLoginResponse> => {
    console.log(`Logging in with email: ${userCrendentials.email}`);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          access_token: "mock_access_token",
          expiration_date: "2025-10-01T00:00:00Z",
          user: {
            id: mockUserDetail.id,
            email: mockUserDetail.email,
            uploaded_resume: mockUserDetail.uploaded_resume,
            name: mockUserDetail.name,
            avatar_url: mockUserDetail.avatar_url,
          },
        });
      }, 100);
    });
  },

  register: async (userData: UserLoginDto): Promise<User> => {
    console.log(`Registering user with email: ${userData.email}`);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: mockUserDetail.id,
          email: userData.email,
          uploaded_resume: false,
          name: mockUserDetail.name,
          avatar_url: mockUserDetail.avatar_url,
        });
      }, 100);
    });
  },

  getCurrentUser: async (): Promise<User> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: mockUserDetail.id,
          email: mockUserDetail.email,
          uploaded_resume: mockUserDetail.uploaded_resume,
          name: mockUserDetail.name,
          avatar_url: mockUserDetail.avatar_url,
        });
      }, 100);
    });
  },
  
  uploadCV: async (file: File): Promise<UploadCVResponse> => {
    console.log(`Uploading CV: ${file.name}`);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          object_key: "resume-123456",
          upload_url: "https://example.com/upload/123456"
        });
      }, 2000);
    });
  },

  processCV: async (objectKey: string): Promise<UserDetail> => {
    console.log(`Processing CV with object key: ${objectKey}`);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockUserDetail);
      }, 3000);
    });
  },
};