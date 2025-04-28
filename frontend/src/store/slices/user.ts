import type { StateCreator } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { IUser } from '../../lib/types/user';

type UserSliceState = {
  user?: IUser;
};

type UserSliceAction = {
  setUser: (user?: IUser) => void;
};

export type UserSlice = UserSliceState & UserSliceAction;

const initialState: UserSliceState = {
  user: undefined,
};

export const createUserSlice: StateCreator<UserSliceState & UserSliceAction, [], [['zustand/immer', never]]> = immer(
  (set) => ({
    ...initialState,
    setUser: (user?: IUser) => {
      set((state) => {
        state.user = user;
      });
    },
  })
);
