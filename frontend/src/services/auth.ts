import api from "./api";
import type { User } from "../types";

interface AuthResponse {
  token: string;
  refresh_token: string;
  user: User;
}

export const authService = {
  async signup(
    email: string,
    password: string,
    full_name: string,
  ): Promise<AuthResponse> {
    const { data } = await api.post("/auth/signup", {
      email,
      password,
      full_name,
    });
    return data;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const { data } = await api.post("/auth/login", { email, password });
    return data;
  },

  async getMe(): Promise<User> {
    const { data } = await api.get("/auth/me");
    return data.user;
  },
};
