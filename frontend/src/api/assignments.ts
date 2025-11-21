import { apiClient } from "./client";
import type { Image } from "./images";
import type { User } from "./users";

export const assignImagesToUser = async (userId: number, imageIds: number[], expires_at?: string) => {
  await apiClient.post(`/assignments/users/${userId}/assign-images`, { image_ids: imageIds, expires_at });
};

export const assignUsersToImage = async (imageId: number, userIds: number[], expires_at?: string) => {
  await apiClient.post(`/assignments/images/${imageId}/assign-users`, { user_ids: userIds, expires_at });
};

export const fetchImagesForUser = async (userId: number): Promise<Image[]> => {
  const { data } = await apiClient.get<Image[]>(`/assignments/users/${userId}/images`);
  return data;
};

export const fetchUsersForImage = async (imageId: number): Promise<User[]> => {
  const { data } = await apiClient.get<User[]>(`/assignments/images/${imageId}/users`);
  return data;
};
