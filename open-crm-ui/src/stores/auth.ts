import { defineStore } from "pinia";
import axios from "axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    username: localStorage.getItem("username") || null,
    error: null as string | null,
    loading: false,
    isAuthenticated: !!localStorage.getItem("token"),
  }),

  actions: {
    async login(username: string, password: string) {
      this.loading = true;
      this.error = null;

      try {
        console.log("[Auth] Login attempt:", username);

        const loginMutation = `
        mutation {
          login(input: {
            username: "${username}"
            password: "${password}"
          }) {
            user {
              id
              userName
              email
            }
            token
          }
        }`;

        const response = await axios.post(
          "http://localhost:5263/graphql",
          {
            query: loginMutation,
          },
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        console.log(
          "[Auth] Login response status:",
          response.status,
          response.data
        );

        if (response.status === 200) {
          const result = response.data;

          if (result.errors) {
            const errorMessage = result.errors[0]?.message;
            console.error("[Auth] GraphQL Error:", errorMessage);
            throw new Error(errorMessage || "GraphQL error occurred");
          }

          if (result.data?.login?.token && result.data?.login?.user?.id) {
            const token = result.data.login.token;
            const userId = result.data.login.user.id;
            const fetchedUsername = result.data.login.user.userName;

            console.log(userId);

            this.token = token;
            this.username = fetchedUsername;
            this.isAuthenticated = true;

            localStorage.setItem("token", token);
            localStorage.setItem("username", fetchedUsername);
            localStorage.setItem("creatorId", userId);

            console.log("[Auth] Login successful, Creator ID:", userId);
            return true;
          } else {
            console.error(
              "[Auth] No token or user ID in response:",
              result.data?.login
            );
            throw new Error("Login response missing token or user ID.");
          }
        } else {
          throw new Error(`HTTP Error: ${response.status}`);
        }
      } catch (error: any) {
        console.error("[Auth] Login failed:", error);
        this.error = error.message || "Login failed";
        this.logout();
        return false;
      } finally {
        this.loading = false;
      }
    },

    logout() {
      this.token = null;
      this.username = null;
      this.error = null;
      this.loading = false;
      this.isAuthenticated = false;
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      localStorage.removeItem("creatorId");
    },
  },
});
