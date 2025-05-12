import { User } from "./user";

export interface IAuthLoginResponse {
  access_token: string;
  expiration_date: string;
  user_info: User;
}

export interface SignUpDto {
  email: string;
  password: string;
}

export interface SignInDto {
  email: string;
  password: string;
}
