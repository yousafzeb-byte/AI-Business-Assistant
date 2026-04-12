import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import type { User } from "../types";
import { authService } from "../services/auth";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token"),
  );
  const [loading, setLoading] = useState(!!token);

  useEffect(() => {
    if (token) {
      authService
        .getMe()
        .then((u) => setUser(u))
        .catch(() => {
          localStorage.removeItem("token");
          localStorage.removeItem("refresh_token");
          setToken(null);
        })
        .finally(() => setLoading(false));
    }
  }, [token]);

  const login = async (email: string, password: string) => {
    const res = await authService.login(email, password);
    localStorage.setItem("token", res.token);
    if (res.refresh_token) {
      localStorage.setItem("refresh_token", res.refresh_token);
    }
    setToken(res.token);
    setUser(res.user);
  };

  const signup = async (email: string, password: string, fullName: string) => {
    const res = await authService.signup(email, password, fullName);
    localStorage.setItem("token", res.token);
    if (res.refresh_token) {
      localStorage.setItem("refresh_token", res.refresh_token);
    }
    setToken(res.token);
    setUser(res.user);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, signup, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
