import { defineStore } from "pinia";
import axios from "axios";
import { useAuthStore } from "./auth";
import type { Comment, CommentFormData } from "@/types/comment";

const API_URL = "http://localhost:5263/api";

export const useCommentStore = defineStore("comments", {
  state: () => ({
    comments: [] as Comment[],
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async getTaskComments(taskId: string) {
      const authStore = useAuthStore();
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.get(
          `${API_URL}/Tasks/${taskId}/Comments`,
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );

        this.comments = response.data;
        return response.data;
      } catch (error: any) {
        console.error("[CommentStore] Error fetching comments:", error);
        this.error =
          error.response?.data?.message || "Failed to fetch comments";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async addComment(taskId: string, commentData: CommentFormData) {
      const authStore = useAuthStore();
      this.loading = true;
      this.error = null;

      try {
        const payload = {
          content: commentData.content,
          createdBy: authStore.username,
          parentCommentId: commentData.parentCommentId,
        };

        const response = await axios.post(
          `${API_URL}/Tasks/${taskId}/Comments`,
          payload,
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );

        // Refresh comments list
        await this.getTaskComments(taskId);
        return response.data;
      } catch (error: any) {
        console.error("[CommentStore] Error adding comment:", error);
        this.error = error.response?.data?.message || "Failed to add comment";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateComment(taskId: string, commentId: number, content: string) {
      const authStore = useAuthStore();
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.put(
          `${API_URL}/Tasks/${taskId}/Comments/${commentId}`,
          { content },
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );

        // Refresh comments list
        await this.getTaskComments(taskId);
        return response.data;
      } catch (error: any) {
        console.error("[CommentStore] Error updating comment:", error);
        this.error =
          error.response?.data?.message || "Failed to update comment";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteComment(taskId: string, commentId: number) {
      const authStore = useAuthStore();
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.delete(
          `${API_URL}/Tasks/${taskId}/Comments/${commentId}`,
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );

        // Refresh comments list
        await this.getTaskComments(taskId);
        return response.status === 204;
      } catch (error: any) {
        console.error("[CommentStore] Error deleting comment:", error);
        this.error =
          error.response?.data?.message || "Failed to delete comment";
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
