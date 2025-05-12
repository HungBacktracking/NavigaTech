import type { StateCreator } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { User } from '../../lib/types/user';

type UserSliceState = {
  user?: User;
};

type UserSliceAction = {
  setUser: (user?: User) => void;
};

export type UserSlice = UserSliceState & UserSliceAction;

const initialState: UserSliceState = {
  user: undefined,
};

export const createUserSlice: StateCreator<UserSliceState & UserSliceAction, [], [['zustand/immer', never]]> = immer(
  (set) => ({
    ...initialState,
    setUser: (user?: User) => {
      set((state) => {
        state.user = user;
      });
    },
  })
);
