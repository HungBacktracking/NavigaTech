import { IUser } from "./user";

export interface IAuthLoginResponse {
  access_token: string;
  refresh_token: string;
  user: IUser;
}
