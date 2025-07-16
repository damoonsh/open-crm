```vue
<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>Workspaces</h1>
        <v-list>
          <v-list-item
            v-for="workspace in workspaces"
            :key="workspace.id"
            :to="`/workspace/${workspace.id}`"
          >
            <v-list-item-content>
              <v-list-item-title>{{ workspace.name }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useAuthStore } from '@/stores/auth'

export default defineComponent({
  name: 'HomePage',
  data() {
    return {
      workspaces: [] as { id: string; name: string }[],
    };
  },
  async mounted() {
    const auth = getAuth();
    const user = auth.currentUser;
    if (user) {
      // Mock API call to fetch workspaces for the logged-in user
      this.workspaces = await this.fetchWorkspaces(user.uid);
    }
  },
  methods: {
    async fetchWorkspaces(userId: string) {
      // Replace with actual API call to fetch workspaces
      return [
        { id: '1', name: 'Project Alpha' },
        { id: '2', name: 'Project Beta' },
      ];
    },
  },
});
</script>
```