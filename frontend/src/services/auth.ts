import { IAuthLoginResponse } from "../lib/types/auth";
import { User, UserDetail, UserLoginDto } from "../lib/types/user";
import api from "../lib/clients/axios/api";

export interface UploadCVResponse {
  object_key: string;
  upload_url: string;
}

export interface DownloadCVResponse {
  download_url: string;
}

export const authApi = {
  login: async (userCredentials: UserLoginDto): Promise<IAuthLoginResponse> => {
    const response = await api.post('/auth/sign-in', userCredentials);  
    return response.data;
  },

  register: async (userData: UserLoginDto): Promise<IAuthLoginResponse> => {
    const response = await api.post('/auth/sign-up', userData);
    console.log(`Registration response: ${response.data}`);
    
    const loginResponse = await authApi.login({
      email: userData.email,
      password: userData.password,
    });
    return loginResponse;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me');
    return response.data;
  },
  
  uploadCV: async (file: File): Promise<UploadCVResponse> => {
    console.log(`Uploading CV: ${file.name}`);
    
    // Step 1: Get upload URL from backend
    const uploadResponse = await api.post('/resumes/upload', {}, {
      params: { file_type: "resume" }
    });
    const { object_key, upload_url } = uploadResponse.data;
    
    // Step 2: Upload the file directly to the storage using the pre-signed URL
    const uploadFileRes = await fetch(upload_url, {
      method: 'PUT',
      headers: {
        'Content-Type': file.type,
      },
      body: file
    });
    console.log(`File upload response: ${uploadFileRes}`);
    
    return { object_key, upload_url };
  },

  processCV: async (): Promise<UserDetail> => {
    const response = await api.post('/resumes/process');
    return response.data;
  },
  
  downloadCV: async (): Promise<DownloadCVResponse> => {
    const response = await api.get('/resumes/download', {
      params: { file_type: "resume" }
    });
    return response.data;
  }
};
