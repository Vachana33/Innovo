import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../../contexts/AuthContext";
import { apiPost } from "../../utils/api";
import styles from "./LoginPage.module.css";

import logo from "../../assets/innovo-logo.png";
import bgImage from "../../assets/login-bg.jpg";

type AuthResponse = {
  success?: boolean;
  access_token?: string;
  message?: string;
};

function isValidEmail(email: string): boolean {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!pattern.test(email)) return false;

  const emailLower = email.toLowerCase();
  if (emailLower === "donotreply@aiio.de") return true;

  return (
    emailLower.endsWith("@innovo-consulting.de") ||
    emailLower.endsWith("@aiio.de")
  );
}

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useContext(AuthContext);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/projects", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!isValidEmail(email)) {
      setError("Email must end with @innovo-consulting.de or @aiio.de");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setIsLoading(true);

    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";

      const data = await apiPost<AuthResponse>(endpoint, {
        email: email.toLowerCase(),
        password,
      });

      if (data.success) {
        if (mode === "login") {
          if (!data.access_token) {
            setError("No token received from server.");
          } else {
            login(data.access_token);
          }
        } else {
          setSuccess("Account created successfully. Please log in.");
          setEmail("");
          setPassword("");
          setMode("login");
        }
      } else {
        setError(data.message ?? "Authentication failed.");
      }
    } catch {
      setError("Network error. Is the backend running?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div
      className={styles.container}
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <img src={logo} alt="Innovo Logo" className={styles.logo} />

      <div className={styles.box}>
        <h1 className={styles.title}>Innovo Agent Login</h1>
        <p className={styles.subtitle}>
          Internal workspace for funding projects.
        </p>

        <div className={styles.modeSwitch}>
          <button
            className={mode === "login" ? styles.activeTab : styles.inactiveTab}
            onClick={() => setMode("login")}
            type="button"
          >
            Login
          </button>
          <button
            className={mode === "signup" ? styles.activeTab : styles.inactiveTab}
            onClick={() => setMode("signup")}
            type="button"
          >
            Create Account
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <label className={styles.label}>Email</label>
          <input
            className={styles.input}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@innovo-consulting.de"
          />

          <label className={styles.label}>Password</label>
          <input
            className={styles.input}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />

          {error && <p className={styles.error}>{error}</p>}
          {success && <p className={styles.success}>{success}</p>}

          <button className={styles.submit} type="submit" disabled={isLoading}>
            {isLoading
              ? "Processing..."
              : mode === "login"
              ? "Login"
              : "Create Account"}
          </button>
        </form>

        <p className={styles.note}>
          Only @innovo-consulting.de or @aiio.de emails are allowed.
        </p>
      </div>
    </div>
  );
}
