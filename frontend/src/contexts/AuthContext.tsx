import { createContext, useState, useEffect, ReactNode } from "react";

interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  token: null,
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
});

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("innovo_auth_token")
  );
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!token);

  const login = (token: string) => {
    localStorage.setItem("innovo_auth_token", token);
    setToken(token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem("innovo_auth_token");
    setToken(null);
    setIsAuthenticated(false);
  };

  useEffect(() => {
    setIsAuthenticated(!!token);
  }, [token]);

  return (
    <AuthContext.Provider
      value={{ token, isAuthenticated, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}
