import { apiClient } from "./client";

export type Status = "active" | "disabled";

export interface User {
  id: number;
  username: string;
  status: Status;
  expires_at?: string;
  extended_until?: string;
  notes?: string;
  created_at: string;
}

export interface CreateUserDto {
  username: string;
  password: string;
  status?: Status;
  expires_at?: string | null;
  notes?: string | null;
}

export interface UpdateUserDto {
  password?: string;
  status?: Status;
  expires_at?: string | null;
  notes?: string | null;
}

export const fetchUsers = async (): Promise<User[]> => {
  const { data } = await apiClient.get<User[]>("/users");
  return data;
};

export const createUser = async (payload: CreateUserDto): Promise<User> => {
  const { data } = await apiClient.post<User>("/users", payload);
  return data;
};

export const updateUser = async (id: number, payload: UpdateUserDto): Promise<User> => {
  const { data } = await apiClient.patch<User>(`/users/${id}`, payload);
  return data;
};

export const extendUser = async (id: number, new_expires_at: string, reason?: string): Promise<User> => {
  const { data } = await apiClient.post<User>(`/users/${id}/extend`, { new_expires_at, reason });
  return data;
};

export const resetPassword = async (id: number, password: string): Promise<User> => {
  const { data } = await apiClient.post<User>(`/users/${id}/reset_password`, { password });
  return data;
};
