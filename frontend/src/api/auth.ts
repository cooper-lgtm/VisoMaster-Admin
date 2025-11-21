import { apiClient } from "./client";

export type LoginPayload = { username: string; password: string };
export type TokenResponse = { access_token: string; token_type: string };

export const adminLogin = async (payload: LoginPayload): Promise<TokenResponse> => {
  const { data } = await apiClient.post<TokenResponse>("/auth/admin/login", payload);
  return data;
};
