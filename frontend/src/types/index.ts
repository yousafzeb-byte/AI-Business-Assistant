export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
}

export interface ExtractedData {
  dates: string[];
  costs: { description: string; amount: number }[];
  tasks: string[];
  deadlines: string[];
  people: string[];
  key_terms: string[];
}

export interface ActionItem {
  action: string;
  priority: "high" | "medium" | "low";
  due: string | null;
  record_id?: number;
  record_title?: string;
}

export interface Record {
  id: number;
  user_id: number;
  title: string;
  input_type: "text" | "file";
  original_content: string;
  file_name: string | null;
  summary: string | null;
  extracted_data: ExtractedData | null;
  action_items: ActionItem[] | null;
  category: string | null;
  total_cost: number | null;
  due_date: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AnalyticsSummary {
  total_records: number;
  total_expenses: number;
  categories: { [key: string]: number };
  statuses: { [key: string]: number };
  pending_actions: ActionItem[];
}

export interface PaginatedRecords {
  records: Record[];
  total: number;
  page: number;
  pages: number;
}
