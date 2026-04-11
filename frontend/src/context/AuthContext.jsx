import { createContext, useContext, useState, useEffect } from "react";
import { auth as authApi } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("hm_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("hm_token");
    if (!token) {
      setLoading(false);
      return;
    }
    authApi.me()
      .then((u) => { setUser(u); localStorage.setItem("hm_user", JSON.stringify(u)); })
      .catch(() => { localStorage.removeItem("hm_token"); localStorage.removeItem("hm_user"); setUser(null); })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const res = await authApi.login({ email, password });
    localStorage.setItem("hm_token", res.token);
    localStorage.setItem("hm_user", JSON.stringify(res.user));
    setUser(res.user);
    return res.user;
  };

  const register = async (name, email, password) => {
    const res = await authApi.register({ name, email, password });
    localStorage.setItem("hm_token", res.token);
    localStorage.setItem("hm_user", JSON.stringify(res.user));
    setUser(res.user);
    return res.user;
  };

  const logout = () => {
    localStorage.removeItem("hm_token");
    localStorage.removeItem("hm_user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
