import { apiClient } from "./client";

export interface Image {
  id: number;
  bucket: string;
  key: string;
  filename: string;
  mime_type?: string;
  size_bytes?: number;
  checksum_sha256?: string;
  uploader_admin_id?: number;
  created_at: string;
  presigned_url?: string;
}

export interface UploadUrlRequest {
  filename: string;
  content_type?: string;
  directory?: string;
}

export interface UploadUrlResponse {
  url: string;
  bucket: string;
  key: string;
}

export interface SaveImageDto {
  bucket: string;
  key: string;
  filename: string;
  mime_type?: string;
  size_bytes?: number;
  checksum_sha256?: string;
}

export const requestUploadUrl = async (payload: UploadUrlRequest): Promise<UploadUrlResponse> => {
  const { data } = await apiClient.post<UploadUrlResponse>("/images/upload-url", payload);
  return data;
};

export const saveImageMetadata = async (payload: SaveImageDto): Promise<Image> => {
  const { data } = await apiClient.post<Image>("/images", payload);
  return data;
};

export const fetchImages = async (): Promise<Image[]> => {
  const { data } = await apiClient.get<Image[]>("/images", { params: { include_urls: true } });
  return data;
};

export const deleteImage = async (id: number): Promise<void> => {
  await apiClient.delete(`/images/${id}`);
};
