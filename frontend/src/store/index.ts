import { create } from 'zustand';

import { createUserSlice, UserSlice } from './slices/user';

type AppStore = UserSlice;

const useAppStore = create<AppStore>((...args) => ({
  ...createUserSlice(...args),
}));

export default useAppStore;
