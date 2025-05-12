import { User } from "./user";

export interface IAuthLoginResponse {
  access_token: string;
  expiration_date: string;
  user: User;
}
