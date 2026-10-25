import { createContext, useContext, useState, ReactNode } from "react";
import { api, getToken, setToken } from "./api";

type Ctx = {
  authed: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (company_name: string, name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
};
const AuthCtx = createContext<Ctx>(null as unknown as Ctx);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState(!!getToken());
  const login = async (email: string, password: string) => {
    const d = await api("/auth/login", "POST", { email, password });
    setToken(d.access_token);
    setAuthed(true);
  };
  const register = async (company_name: string, name: string, email: string, password: string) => {
    await api("/auth/register", "POST", { company_name, name, email, password });
    await login(email, password);
  };
  const logout = () => { setToken(null); setAuthed(false); };
  return <AuthCtx.Provider value={{ authed, login, register, logout }}>{children}</AuthCtx.Provider>;
}
