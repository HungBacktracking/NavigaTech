export interface IUser {
  email: string;
  cvUploaded?: boolean;
}

export type UserLoginDto = {
  email: string;
  password: string;
};
