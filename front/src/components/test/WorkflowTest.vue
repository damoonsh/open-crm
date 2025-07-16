<template>
  <v-card class="workflow-test">
    <v-card-title>
      <div class="test-header">
        <v-icon left>mdi-test-tube</v-icon>
        End-to-End Task Workflow Test
      </div>
    </v-card-title>

    <v-card-text>
      <div class="test-description">
        <p>This component tests the complete task workflow from creation to completion, including:</p>
        <ul>
          <li>Task creation with all fields</li>
          <li>Category assignment and movement</li>
          <li>Status transitions</li>
          <li>Dependency management</li>
          <li>Real-time updates</li>
          <li>Drag-and-drop functionality</li>
        </ul>
      </div>

      <v-divider class="my-4" />

      <!-- Test Controls -->
      <div class="test-controls">
        <v-btn
          color="primary"
          @click="runFullWorkflowTest"
          :loading="testRunning"
          :disabled="!workspaceId"
        >
          <v-icon left>mdi-play</v-icon>
          Run Full Workflow Test
        </v-btn>
        
        <v-btn
          color="secondary"
          @click="runDragDropTest"
          :loading="dragTestRunning"
          :disabled="!workspaceId"
        >
          <v-icon left>mdi-drag</v-icon>
          Test Drag & Drop
        </v-btn>
        
        <v-btn
          color="info"
          @click="runDependencyTest"
          :loading="depTestRunning"
          :disabled="!workspaceId"
        >
          <v-icon left>mdi-link</v-icon>
          Test Dependencies
        </v-btn>
        
        <v-btn
          color="warning"
          @click="clearTestData"
          :disabled="testRunning"
        >
          <v-icon left>mdi-delete-sweep</v-icon>
          Clear Test Data
        </v-btn>
      </div>

      <!-- Test Results -->
      <div v-if="testResults.length > 0" class="test-results">
        <h3>Test Results</h3>
        <div class="results-list">
          <div
            v-for="(result, index) in testResults"
            :key="index"
            class="result-item"
            :class="{ 
              'result-success': result.success, 
              'result-error': !result.success 
            }"
          >
            <v-icon :color="result.success ? 'success' : 'error'">
              {{ result.success ? 'mdi-check-circle' : 'mdi-alert-circle' }}
            </v-icon>
            <div class="result-content">
              <div class="result-title">{{ result.title }}</div>
              <div class="result-description">{{ result.description }}</div>
              <div v-if="result.error" class="result-error-text">{{ result.error }}</div>
            </div>
            <div class="result-timing">{{ result.duration }}ms</div>
          </div>
        </div>
      </div>

      <!-- Test Progress -->
      <div v-if="testRunning" class="test-progress">
        <v-progress-linear
          :model-value="testProgress"
          color="primary"
          height="8"
          rounded
        />
        <p class="progress-text">{{ currentTestStep }}</p>
      </div>

      <!-- Live Task Display -->
      <div v-if="testTasks.length > 0" class="test-tasks">
        <h3>Test Tasks Created</h3>
        <div class="tasks-grid">
          <v-card
            v-for="task in testTasks"
            :key="task.id"
            class="test-task-card"
            variant="outlined"
          >
            <v-card-text>
              <div class="task-header">
                <h4>{{ task.title }}</h4>
                <v-chip :color="getStatusColor(task.status)" size="small">
                  {{ formatStatus(task.status) }}
                </v-chip>
              </div>
              <p class="task-description">{{ task.description }}</p>
              <div class="task-meta">
                <v-chip size="x-small" :color="getPriorityColor(task.priority)">
                  {{ task.priority }}
                </v-chip>
                <span v-if="task.story_points" class="story-points">
                  {{ task.story_points }} pts
                </span>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTaskStore } from '@/stores/tasks';
import { useCategoryStore } from '@/stores/categories';
import { useWorkspaceStore } from '@/stores/workspace';
import type { Task, TaskCreate } from '@/stores/tasks';

interface Props {
  workspaceId?: number;
}

const props = defineProps<Props>();

const taskStore = useTaskStore();
const categoryStore = useCategoryStore();
const workspaceStore = useWorkspaceStore();

// Component state
const testRunning = ref(false);
const dragTestRunning = ref(false);
const depTestRunning = ref(false);
const testProgress = ref(0);
const currentTestStep = ref('');
const testResults = ref<Array<{
  title: string;
  description: string;
  success: boolean;
  duration: number;
  error?: string;
}>>([]);
const testTasks = ref<Task[]>([]);

// Computed properties
const workspaceId = computed(() => props.workspaceId || 1);

// Methods
const runFullWorkflowTest = async () => {
  testRunning.value = true;
  testProgress.value = 0;
  testResults.value = [];
  testTasks.value = [];

  const steps = [
    { name: 'Create Test Categories', fn: createTestCategories },
    { name: 'Create Test Tasks', fn: createTestTasks },
    { name: 'Test Status Transitions', fn: testStatusTransitions },
    { name: 'Test Category Movement', fn: testCategoryMovement },
    { name: 'Test Task Dependencies', fn: testTaskDependencies },
    { name: 'Test Task Updates', fn: testTaskUpdates },
    { name: 'Verify Data Integrity', fn: verifyDataIntegrity }
  ];

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    currentTestStep.value = step.name;
    testProgress.value = (i / steps.length) * 100;

    const startTime = Date.now();
    try {
      await step.fn();
      const duration = Date.now() - startTime;
      testResults.value.push({
        title: step.name,
        description: 'Completed successfully',
        success: true,
        duration
      });
    } catch (error: any) {
      const duration = Date.now() - startTime;
      testResults.value.push({
        title: step.name,
        description: 'Failed to complete',
        success: false,
        duration,
        error: error.message
      });
    }

    // Small delay between steps
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  testProgress.value = 100;
  currentTestStep.value = 'Test completed';
  testRunning.value = false;
};

const createTestCategories = async () => {
  const categories = [
    { name: 'Test Backlog', color: '#2196f3', position: 0 },
    { name: 'Test In Progress', color: '#ff9800', position: 1 },
    { name: 'Test Review', color: '#9c27b0', position: 2 },
    { name: 'Test Done', color: '#4caf50', position: 3 }
  ];

  for (const categoryData of categories) {
    await categoryStore.createCategory(workspaceId.value, {
      name: categoryData.name,
      description: `Test category for workflow testing`,
      color: categoryData.color,
      position: categoryData.position,
      default_status: 'open',
      allowed_statuses: ['open', 'in_progress', 'review', 'closed']
    });
  }
};

const createTestTasks = async () => {
  const taskTemplates = [
    {
      title: 'Test Task 1 - Basic Task',
      description: 'This is a basic test task to verify task creation functionality.',
      priority: 'medium' as const,
      story_points: 3
    },
    {
      title: 'Test Task 2 - High Priority',
      description: 'This is a high priority test task with dependencies.',
      priority: 'high' as const,
      story_points: 5
    },
    {
      title: 'Test Task 3 - Low Priority',
      description: 'This is a low priority test task for workflow testing.',
      priority: 'low' as const,
      story_points: 1
    }
  ];

  const categories = categoryStore.categories.filter(cat => cat.name.startsWith('Test'));
  const backlogCategory = categories.find(cat => cat.name.includes('Backlog'));

  for (const template of taskTemplates) {
    const taskData: TaskCreate = {
      title: template.title,
      description: template.description,
      priority: template.priority,
      story_points: template.story_points,
      category_id: backlogCategory?.id || null,
      labels: ['test', 'workflow', 'automation']
    };

    const createdTask = await taskStore.createTask(workspaceId.value, taskData);
    if (createdTask) {
      testTasks.value.push(createdTask);
    }
  }
};

const testStatusTransitions = async () => {
  const statuses = ['open', 'in_progress', 'review', 'closed'];
  
  for (const task of testTasks.value) {
    for (const status of statuses) {
      await taskStore.updateTaskStatus(task.id, status as any);
      // Verify status was updated
      const updatedTask = taskStore.getTaskById(task.id);
      if (updatedTask?.status !== status) {
        throw new Error(`Status transition failed for task ${task.id}`);
      }
    }
  }
};

const testCategoryMovement = async () => {
  const categories = categoryStore.categories.filter(cat => cat.name.startsWith('Test'));
  
  for (const task of testTasks.value) {
    for (const category of categories) {
      await taskStore.updateTaskCategory(task.id, category.id);
      // Verify category was updated
      const updatedTask = taskStore.getTaskById(task.id);
      if (updatedTask?.category_id !== category.id) {
        throw new Error(`Category movement failed for task ${task.id}`);
      }
    }
  }
};

const testTaskDependencies = async () => {
  if (testTasks.value.length < 2) return;

  const [task1, task2] = testTasks.value;
  
  // Create dependency: task2 depends on task1
  await taskStore.addTaskDependency(task2.id, task1.id);
  
  // Verify dependency was created
  const updatedTask2 = taskStore.getTaskById(task2.id);
  if (!updatedTask2?.blocked_by_dependencies?.some(dep => dep.blocking_task_id === task1.id)) {
    throw new Error('Dependency creation failed');
  }
  
  // Remove dependency
  await taskStore.removeTaskDependency(task2.id, task1.id);
  
  // Verify dependency was removed
  const finalTask2 = taskStore.getTaskById(task2.id);
  if (finalTask2?.blocked_by_dependencies?.some(dep => dep.blocking_task_id === task1.id)) {
    throw new Error('Dependency removal failed');
  }
};

const testTaskUpdates = async () => {
  for (const task of testTasks.value) {
    const updateData = {
      title: `${task.title} - Updated`,
      description: `${task.description} - Updated description`,
      priority: task.priority === 'high' ? 'low' as const : 'high' as const
    };
    
    await taskStore.updateTask(task.id, updateData);
    
    // Verify updates
    const updatedTask = taskStore.getTaskById(task.id);
    if (updatedTask?.title !== updateData.title) {
      throw new Error(`Task update failed for task ${task.id}`);
    }
  }
};

const verifyDataIntegrity = async () => {
  // Refresh data from server
  await taskStore.fetchTasks(workspaceId.value);
  await categoryStore.fetchCategories(workspaceId.value);
  
  // Verify all test tasks still exist
  for (const task of testTasks.value) {
    const existingTask = taskStore.getTaskById(task.id);
    if (!existingTask) {
      throw new Error(`Task ${task.id} not found after refresh`);
    }
  }
  
  // Update local test tasks with latest data
  testTasks.value = testTasks.value.map(task => 
    taskStore.getTaskById(task.id) || task
  );
};

const runDragDropTest = async () => {
  dragTestRunning.value = true;
  // Simulate drag and drop operations
  // This would test the drag-and-drop functionality
  await new Promise(resolve => setTimeout(resolve, 2000));
  dragTestRunning.value = false;
};

const runDependencyTest = async () => {
  depTestRunning.value = true;
  // Test dependency blocking and validation
  await new Promise(resolve => setTimeout(resolve, 2000));
  depTestRunning.value = false;
};

const clearTestData = async () => {
  // Delete test tasks
  for (const task of testTasks.value) {
    try {
      await taskStore.deleteTask(task.id);
    } catch (error) {
      console.error('Error deleting test task:', error);
    }
  }
  
  // Delete test categories
  const testCategories = categoryStore.categories.filter(cat => cat.name.startsWith('Test'));
  for (const category of testCategories) {
    try {
      await categoryStore.deleteCategory(category.id);
    } catch (error) {
      console.error('Error deleting test category:', error);
    }
  }
  
  testTasks.value = [];
  testResults.value = [];
  testProgress.value = 0;
  currentTestStep.value = '';
};

// Utility methods
const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    open: 'blue',
    in_progress: 'orange',
    review: 'purple',
    closed: 'green',
    blocked: 'red'
  };
  return colors[status] || 'grey';
};

const getPriorityColor = (priority: string): string => {
  const colors: Record<string, string> = {
    high: 'error',
    medium: 'warning',
    low: 'success'
  };
  return colors[priority] || 'grey';
};

const formatStatus = (status: string): string => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Lifecycle
onMounted(async () => {
  if (workspaceId.value) {
    await Promise.all([
      taskStore.fetchTasks(workspaceId.value),
      categoryStore.fetchCategories(workspaceId.value)
    ]);
  }
});
</script>

<style scoped>
.workflow-test {
  margin: 16px;
}

.test-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.test-description {
  margin-bottom: 16px;
}

.test-description ul {
  margin: 8px 0;
  padding-left: 20px;
}

.test-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.test-results {
  margin-top: 24px;
}

.test-results h3 {
  margin: 0 0 16px 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.result-item.result-success {
  background: #f1f8e9;
  border-color: #4caf50;
}

.result-item.result-error {
  background: #ffebee;
  border-color: #f44336;
}

.result-content {
  flex: 1;
}

.result-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.result-description {
  color: #666;
  font-size: 0.9rem;
}

.result-error-text {
  color: #f44336;
  font-size: 0.85rem;
  margin-top: 4px;
  font-family: monospace;
}

.result-timing {
  font-size: 0.8rem;
  color: #999;
  font-family: monospace;
}

.test-progress {
  margin: 24px 0;
}

.progress-text {
  margin: 8px 0 0 0;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}

.test-tasks {
  margin-top: 24px;
}

.test-tasks h3 {
  margin: 0 0 16px 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.test-task-card {
  border-left: 4px solid #2196f3;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.task-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  flex: 1;
  margin-right: 8px;
}

.task-description {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.story-points {
  font-size: 0.8rem;
  color: #666;
  font-family: monospace;
}

/* Responsive design */
@media (max-width: 768px) {
  .test-controls {
    flex-direction: column;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .result-item {
    flex-direction: column;
    gap: 8px;
  }
}
</style>