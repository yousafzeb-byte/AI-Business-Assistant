import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ProtectedRoute from "../components/ProtectedRoute";
import { AuthProvider } from "../context/AuthContext";

describe("ProtectedRoute", () => {
  it("redirects to login when not authenticated", () => {
    // Clear any token
    localStorage.removeItem("token");
    const { container } = render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <AuthProvider>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </AuthProvider>
      </MemoryRouter>,
    );
    // Should not show protected content (redirects to login)
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });
});
