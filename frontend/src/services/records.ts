import api from "./api";
import type { Record, PaginatedRecords, AnalyticsSummary } from "../types";

export const recordsService = {
  async create(content: string, title: string): Promise<Record> {
    const { data } = await api.post("/records", { content, title });
    return data.record;
  },

  async uploadFile(file: File, title: string): Promise<Record> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    const { data } = await api.post("/records", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data.record;
  },

  async list(params: {
    page?: number;
    per_page?: number;
    search?: string;
    category?: string;
    status?: string;
  }): Promise<PaginatedRecords> {
    const { data } = await api.get("/records", { params });
    return data;
  },

  async get(id: number): Promise<Record> {
    const { data } = await api.get(`/records/${id}`);
    return data.record;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/records/${id}`);
  },

  async updateStatus(id: number, status: string): Promise<Record> {
    const { data } = await api.patch(`/records/${id}/status`, { status });
    return data.record;
  },

  async update(
    id: number,
    fields: { title?: string; category?: string },
  ): Promise<Record> {
    const { data } = await api.patch(`/records/${id}`, fields);
    return data.record;
  },
};

export const analyticsService = {
  async getSummary(): Promise<AnalyticsSummary> {
    const { data } = await api.get("/analytics/summary");
    return data;
  },
};
