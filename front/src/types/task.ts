export enum Status {
  Pending = "PENDING",
  InProgress = "IN_PROGRESS",
  Completed = "COMPLETED",
  OnHold = "ON_HOLD",
  Cancelled = "CANCELLED",
}

export enum Priority {
  Low = "LOW",
  Medium = "MEDIUM",
  High = "HIGH",
  Urgent = "URGENT",
}

export interface Task {
  id: number;
  title: string;
  description: string;
  status: string;
  dueDate?: string;
  creatorId: string;
  priority: string | null;
  category?: string;
  tags?: string[];
  createdAt: string;
  lastUpdated: string;
}

export interface TaskFormData {
  title: string;
  description: string;
  status: Status | string;
  priority: Priority | string | null;
  category?: string;
  tags: string[];
  dueDate?: string;
}

export interface EditState {
  isEditing: boolean;
  taskId: number | null;
  form: TaskFormData;
}
