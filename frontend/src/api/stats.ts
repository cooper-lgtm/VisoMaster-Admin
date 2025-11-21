import { apiClient } from "./client";

export interface StatsSummary {
  total_users: number;
  active_users: number;
  disabled_users: number;
  expiring_users: number;
  total_images: number;
}

export const fetchStats = async (): Promise<StatsSummary> => {
  const { data } = await apiClient.get<StatsSummary>("/stats/summary");
  return data;
};
