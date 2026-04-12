import { describe, it, expect } from "vitest";
import type {
  User,
  Record,
  AnalyticsSummary,
  PaginatedRecords,
} from "../types";

describe("TypeScript interfaces", () => {
  it("User interface has required fields", () => {
    const user: User = {
      id: 1,
      email: "test@test.com",
      full_name: "Test User",
      role: "user",
      created_at: "2024-01-01T00:00:00",
    };
    expect(user.id).toBe(1);
    expect(user.email).toBe("test@test.com");
  });

  it("Record interface has required fields", () => {
    const record: Record = {
      id: 1,
      user_id: 1,
      title: "Test",
      input_type: "text",
      original_content: "content",
      file_name: null,
      summary: "summary",
      extracted_data: null,
      action_items: null,
      category: "note",
      total_cost: null,
      due_date: null,
      status: "processed",
      created_at: "2024-01-01T00:00:00",
      updated_at: "2024-01-01T00:00:00",
    };
    expect(record.title).toBe("Test");
    expect(record.status).toBe("processed");
  });

  it("AnalyticsSummary interface has required fields", () => {
    const summary: AnalyticsSummary = {
      total_records: 5,
      total_expenses: 100.5,
      categories: { invoice: 3, note: 2 },
      statuses: { processed: 4, pending: 1 },
      pending_actions: [],
    };
    expect(summary.total_records).toBe(5);
    expect(summary.categories.invoice).toBe(3);
  });

  it("PaginatedRecords interface has required fields", () => {
    const paginated: PaginatedRecords = {
      records: [],
      total: 0,
      page: 1,
      pages: 0,
    };
    expect(paginated.total).toBe(0);
    expect(paginated.page).toBe(1);
  });
});
