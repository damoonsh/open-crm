export interface Comment {
  id: number;
  taskId: number;
  content: string;
  createdBy: string;
  createdAt: string;
  lastUpdated?: string;
  parentCommentId?: number;
  replies?: Comment[];
}

export interface CommentFormData {
  content: string;
  parentCommentId?: number;
}

export interface AddCommentInput {
  taskId: number;
  content: string;
  createdBy: string;
  parentCommentId?: number;
}

export interface UpdateCommentInput {
  id: number;
  content: string;
}
