import { create } from "zustand";
import { persist } from "zustand/middleware";

type AdminInfo = {
  username: string;
  is_superadmin?: boolean;
};

type AuthState = {
  token: string | null;
  admin: AdminInfo | null;
  setToken: (token: string, admin?: AdminInfo) => void;
  logout: () => void;
};

export const authStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      admin: null,
      setToken: (token, admin) => set({ token, admin: admin ?? null }),
      logout: () => set({ token: null, admin: null }),
    }),
    { name: "vm-admin-auth" },
  ),
);
