import { useState, type FormEvent } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { Brain } from "lucide-react";
import { authService } from "../services/auth";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!token) {
      setError("Missing reset token. Please use the link from your email.");
      return;
    }

    setLoading(true);
    try {
      const res = await authService.resetPassword(token, password);
      setMessage(res.message);
      setTimeout(() => navigate("/login"), 3000);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: string } } })?.response?.data
          ?.error || "Failed to reset password. The link may have expired.";
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
          <p>Set a new password</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {message && (
          <div className="alert alert-success">
            {message} Redirecting to login...
          </div>
        )}

        {!message && (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="password">New Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                placeholder="••••••••"
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={loading}
            >
              {loading ? "Resetting..." : "Reset Password"}
            </button>
          </form>
        )}

        <p className="auth-footer">
          <Link to="/login">Back to Sign In</Link>
        </p>
      </div>
    </div>
  );
}
