import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { Brain } from "lucide-react";
import { authService } from "../services/auth";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);
    try {
      const res = await authService.forgotPassword(email);
      setMessage(res.message);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: string } } })?.response?.data
          ?.error || "Something went wrong. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <Brain size={36} />
          <h1>AI Business Ops</h1>
          <p>Reset your password</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {message && <div className="alert alert-success">{message}</div>}

        {!message ? (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={loading}
            >
              {loading ? "Sending..." : "Send Reset Link"}
            </button>
          </form>
        ) : (
          <p style={{ textAlign: "center", color: "#666", marginTop: "12px" }}>
            Check your email (or the server logs in dev mode) for the reset
            link.
          </p>
        )}

        <p className="auth-footer">
          Remember your password? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
