import { defineStore } from "pinia";
import axios, { type AxiosResponse } from "axios"; // Import AxiosResponse type
import { useAuthStore } from "./auth";
import type { Task, TaskFormData } from "@/types/task";

const GRAPHQL_URL = "http://localhost:5263/graphql";

// --- Error Handling Helper Functions ---

/**
 * Checks a GraphQL response for errors and updates the store's error state.
 * @param responseData - The data object from the Axios response.
 * @param storeInstance - The Pinia store instance (this).
 * @param actionName - A descriptive name for the action (e.g., "fetchTasks").
 * @returns `true` if GraphQL errors were found, `false` otherwise.
 */
function handleGraphQLResponseErrors(
  responseData: any,
  storeInstance: { error: string | null }, // Type for store instance part we need
  actionName: string
): boolean {
  if (responseData?.errors && responseData.errors.length > 0) {
    const errorMessage =
      responseData.errors[0]?.message || `Failed to ${actionName} via GraphQL`;
    console.error(`GraphQL Errors (${actionName}):`, responseData.errors);
    storeInstance.error = errorMessage;
    return true; // Errors found
  }
  return false; // No errors found
}

/**
 * Handles errors caught during an action (e.g., network errors).
 * @param error - The error object caught.
 * @param storeInstance - The Pinia store instance (this).
 * @param actionName - A descriptive name for the action.
 * @param defaultErrorMessage - A fallback error message.
 */
function handleActionError(
  error: any,
  storeInstance: { error: string | null }, // Type for store instance part we need
  actionName: string,
  defaultErrorMessage: string
) {
  console.error(`Task ${actionName} error:`, error.response || error);
  // Only set the error if it wasn't already set by handleGraphQLResponseErrors
  if (!storeInstance.error) {
    storeInstance.error =
      error.response?.data?.message || error.message || defaultErrorMessage;
  }
}

// --- Pinia Store Definition ---

export const useTaskStore = defineStore("tasks", {
  state: () => ({
    tasks: [] as Task[],
    loading: false,
    error: null as string | null,
    currentTask: null as Task | null,
  }),

  actions: {
    async fetchTasks() {
      const authStore = useAuthStore();
      this.loading = true;
      this.error = null;
      const actionName = "fetchTasks";

      const query = `
        query GetUserTasks($username: String!) {
          tasksByCreator(username: $username) {
            nodes { id title description status priority dueDate createdAt lastUpdated tags category }
          }
        }
      `;
      const variables = { username: authStore.username };

      try {
        const response = await axios.post(
          GRAPHQL_URL,
          { query, variables },
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (handleGraphQLResponseErrors(response.data, this, actionName)) {
          this.tasks = []; // Clear tasks on GraphQL error
          return; // Exit early
        }

        if (response.data?.data?.tasksByCreator?.nodes) {
          this.tasks = response.data.data.tasksByCreator.nodes;
          console.log("Tasks updated via GraphQL:", this.tasks);
        } else {
          console.warn(
            "No tasks found or unexpected GraphQL response structure:",
            response.data
          );
          this.tasks = [];
        }
      } catch (error: any) {
        handleActionError(error, this, actionName, "Failed to fetch tasks");
        this.tasks = []; // Clear tasks on general error
      } finally {
        this.loading = false;
      }
    },

    async getTask(taskId: string) {
      const authStore = useAuthStore();
      this.loading = true;
      this.error = null;
      this.currentTask = null;
      const actionName = "getTask";

      const query = `
        query GetTaskById($id: Int!) {
          taskById(id: $id) { id title description status priority dueDate createdAt lastUpdated tags category creatorId }
        }
      `;
      const variables = { id: parseInt(taskId) };

      try {
        console.log("Fetching task with variables:", variables);
        const response = await axios.post(
          GRAPHQL_URL,
          { query, variables },
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        console.log("GraphQL API Response Data (getTask):", response.data);

        if (handleGraphQLResponseErrors(response.data, this, actionName)) {
          return; // Exit early
        }

        if (response.data?.data?.taskById) {
          this.currentTask = response.data.data.taskById;
          console.log("Task fetched via GraphQL:", this.currentTask);
          // Optionally update the task in the main list if it exists
          const index = this.tasks.findIndex(
            (t) => t.id === this.currentTask?.id
          );
          if (index !== -1 && this.currentTask) {
            this.tasks[index] = this.currentTask;
          }
        } else {
          console.warn(
            "Task not found or unexpected GraphQL response structure:",
            response.data
          );
          this.error = `Task with ID ${taskId} not found.`; // Specific error for not found
        }
      } catch (error: any) {
        handleActionError(
          error,
          this,
          actionName,
          `Failed to fetch task ${taskId}`
        );
      } finally {
        this.loading = false;
      }
    },

    async createTask(taskData: TaskFormData): Promise<Task | null> {
      const authStore = useAuthStore();
      const actionName = "createTask";

      if (!authStore.username) {
        this.error =
          "Cannot create task: User not logged in or username missing.";
        console.error(this.error);
        return null;
      }

      this.loading = true;
      this.error = null;

      // --- Date Formatting (Keep as is) ---
      let formattedDueDate: string | null = null;
      if (taskData.dueDate) {
        try {
          const date = new Date(taskData.dueDate + "T00:00:00Z");
          if (!isNaN(date.getTime())) {
            formattedDueDate = date.toISOString();
          } else {
            console.warn(`Invalid date string received: ${taskData.dueDate}`);
          }
        } catch (e) {
          console.error(`Error parsing date: ${taskData.dueDate}`, e);
        }
      }
      // --- End Date Formatting ---

      const input = {
        title: taskData.title,
        description: taskData.description || null,
        status: taskData.status.toUpperCase(),
        priority: taskData.priority ? taskData.priority.toUpperCase() : null,
        dueDate: formattedDueDate || null,
        creatorId: authStore.username,
        category: taskData.category || null,
        tags: Array.isArray(taskData.tags)
          ? taskData.tags
          : taskData.tags
          ? [taskData.tags]
          : [],
      };

      const mutation = `
        mutation CreateTask($input: CreateTaskInput!) {
          createTask(input: $input) { id title description status priority dueDate createdAt lastUpdated tags category creatorId }
        }
      `;
      const variables = { input };

      try {
        console.log(
          "Creating task with variables:",
          JSON.stringify(variables, null, 2)
        );
        const response = await axios.post(
          GRAPHQL_URL,
          { query: mutation, variables },
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        console.log("GraphQL API Response Data (createTask):", response.data);

        if (handleGraphQLResponseErrors(response.data, this, actionName)) {
          return null; // Indicate failure
        }

        if (response.data?.data?.createTask) {
          const newTask = response.data.data.createTask;
          this.tasks.unshift(newTask); // Add to the beginning of the list
          console.log("Task created and added to store:", newTask);
          return newTask; // Indicate success
        } else {
          console.warn(
            "Task creation failed or unexpected GraphQL response structure:",
            response.data
          );
          this.error = "Task creation failed.";
          return null; // Indicate failure
        }
      } catch (error: any) {
        handleActionError(error, this, actionName, "Failed to create task");
        return null; // Indicate failure
      } finally {
        this.loading = false;
      }
    },

    async updateTask(
      taskId: number,
      taskData: Partial<TaskFormData>
    ): Promise<Task | null> {
      const authStore = useAuthStore();
      const actionName = "updateTask";

      if (!authStore.username) {
        this.error =
          "Cannot update task: User not logged in or username missing.";
        console.error(this.error);
        return null;
      }
      if (!taskId) {
        this.error = "Cannot update task: Task ID is missing.";
        console.error(this.error);
        return null;
      }

      this.loading = true;
      this.error = null;

      // --- Format dueDate if present ---
      let formattedDueDate: string | undefined | null = undefined; // Use undefined to signal not updating unless provided
      if (taskData.dueDate !== undefined) {
        // Check if dueDate is explicitly provided (even if null)
        if (taskData.dueDate) {
          try {
            const date = new Date(taskData.dueDate + "T00:00:00Z");
            if (!isNaN(date.getTime())) {
              formattedDueDate = date.toISOString();
            } else {
              console.warn(
                `Invalid date string received for update: ${taskData.dueDate}`
              );
              formattedDueDate = null; // Or handle as error? Decide based on requirements.
            }
          } catch (e) {
            console.error(
              `Error parsing date for update: ${taskData.dueDate}`,
              e
            );
            formattedDueDate = null;
          }
        } else {
          formattedDueDate = null; // Explicitly setting dueDate to null
        }
      }
      // --- End date formatting ---

      // Construct the input object dynamically based on provided taskData
      const input: { [key: string]: any } = { id: taskId }; // Always include ID
      if (taskData.title !== undefined) input.title = taskData.title;
      if (taskData.description !== undefined)
        input.description = taskData.description; // Allow setting description to null/empty
      if (taskData.status !== undefined)
        input.status = taskData.status.toUpperCase();
      if (taskData.priority !== undefined)
        input.priority = taskData.priority
          ? taskData.priority.toUpperCase()
          : null;
      if (formattedDueDate !== undefined) input.dueDate = formattedDueDate; // Only include if dueDate was in taskData
      if (taskData.category !== undefined) input.category = taskData.category;
      if (taskData.tags !== undefined) {
        input.tags = Array.isArray(taskData.tags)
          ? taskData.tags
          : taskData.tags
          ? [taskData.tags]
          : [];
      }
      // Note: creatorId is usually not updatable

      // Check if any fields other than 'id' were actually provided for update
      if (Object.keys(input).length <= 1) {
        console.warn("Update task called with no fields to update.");
        this.loading = false;
        // Optionally set an error or just return the current task state if needed
        // this.error = "No fields provided for update.";
        // Find the existing task to return it, or null if not found
        const existingTask =
          this.tasks.find((t) => t.id === taskId) ||
          (this.currentTask?.id === taskId ? this.currentTask : null);
        return existingTask;
      }

      const mutation = `
          mutation UpdateTask($input: UpdateTaskInput!) {
              updateTask(input: $input) {
                  id title description status priority dueDate createdAt lastUpdated tags category creatorId
              }
          }
      `;
      const variables = { input };

      try {
        console.log(
          `Updating task ${taskId} with variables:`,
          JSON.stringify(variables, null, 2)
        );
        const response = await axios.post(
          GRAPHQL_URL,
          { query: mutation, variables },
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        console.log("GraphQL API Response Data (updateTask):", response.data);

        if (handleGraphQLResponseErrors(response.data, this, actionName)) {
          return null; // Indicate failure
        }

        if (response.data?.data?.updateTask) {
          const updatedTask = response.data.data.updateTask;
          // Update the task in the main list
          const index = this.tasks.findIndex((t) => t.id === updatedTask.id);
          if (index !== -1) {
            this.tasks[index] = updatedTask;
          }
          // Update currentTask if it's the one being updated
          if (this.currentTask?.id === updatedTask.id) {
            this.currentTask = updatedTask;
          }
          console.log("Task updated successfully:", updatedTask);
          return updatedTask; // Indicate success
        } else {
          console.warn(
            "Task update failed or unexpected GraphQL response structure:",
            response.data
          );
          this.error = "Task update failed.";
          return null; // Indicate failure
        }
      } catch (error: any) {
        handleActionError(
          error,
          this,
          actionName,
          `Failed to update task ${taskId}`
        );
        return null; // Indicate failure
      } finally {
        this.loading = false;
      }
    },

    async deleteTask(taskId: number): Promise<boolean> {
      const authStore = useAuthStore();
      const actionName = "deleteTask";

      if (!authStore.username) {
        this.error =
          "Cannot delete task: User not logged in or username missing.";
        console.error(this.error);
        return false;
      }

      this.loading = true;
      this.error = null;

      const mutation = `
        mutation DeleteTask($id: Int!, $requestorUsername: String!) {
          deleteTask(id: $id, requestorUsername: $requestorUsername)
        }
      `;
      const variables = { id: taskId, requestorUsername: authStore.username };

      try {
        console.log(
          `Attempting to delete task with ID: ${taskId} by user: ${authStore.username}`
        );
        const response = await axios.post(
          GRAPHQL_URL,
          { query: mutation, variables },
          {
            headers: {
              Authorization: `Bearer ${authStore.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        console.log("GraphQL API Response Data (deleteTask):", response.data);

        if (handleGraphQLResponseErrors(response.data, this, actionName)) {
          // Check for specific authorization errors if possible from extensions
          if (
            response.data.errors[0]?.extensions?.code === "AUTH_NOT_AUTHORIZED"
          ) {
            this.error = "You are not authorized to delete this task.";
          }
          return false; // Indicate failure
        }

        if (response.data?.data?.deleteTask === true) {
          const index = this.tasks.findIndex((t) => t.id === taskId);
          if (index !== -1) {
            this.tasks.splice(index, 1);
          }
          if (this.currentTask?.id === taskId) {
            this.currentTask = null;
          }
          console.log(`Task ${taskId} deleted successfully.`);
          return true; // Indicate success
        } else {
          const specificError =
            response.data?.data?.deleteTask === false
              ? "Deletion rejected by server logic (e.g., permissions)."
              : "Task deletion failed or unexpected GraphQL response.";
          console.warn(specificError, response.data);
          this.error = this.error || specificError; // Keep existing error if already set
          return false; // Indicate failure
        }
      } catch (error: any) {
        handleActionError(error, this, actionName, "Failed to delete task");
        return false; // Indicate failure
      } finally {
        this.loading = false;
      }
    },
  },
});
