import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useAuthStore } from "./auth";

// Types for Category
export interface Category {
  id: number;
  workspace_id: number;
  name: string;
  description?: string;
  color: string;
  position: number;
  is_archived: boolean;
  default_status: string;
  allowed_statuses: string[];
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  description?: string;
  color?: string;
  position?: number;
  default_status?: string;
  allowed_statuses?: string[];
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
  color?: string;
  position?: number;
  is_archived?: boolean;
  default_status?: string;
  allowed_statuses?: string[];
}

export const useCategoryStore = defineStore("categories", () => {
  // State
  const categories = ref<Category[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const currentCategory = ref<Category | null>(null);

  // Getters
  const categoriesByWorkspace = computed(() => {
    return (workspaceId: number) => 
      categories.value
        .filter(cat => cat.workspace_id === workspaceId && !cat.is_archived)
        .sort((a, b) => a.position - b.position);
  });

  const getCategoryById = computed(() => {
    return (categoryId: number) => 
      categories.value.find(cat => cat.id === categoryId);
  });

  // Actions
  const fetchWorkspaceCategories = async (workspaceId: number) => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/categories/workspace/${workspaceId}`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch categories: ${response.statusText}`);
      }

      const data = await response.json();
      categories.value = data;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch categories';
      console.error('Error fetching categories:', err);
    } finally {
      loading.value = false;
    }
  };

  const createCategory = async (workspaceId: number, categoryData: CategoryCreate): Promise<Category | null> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/categories/workspace/${workspaceId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(categoryData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to create category: ${response.statusText}`);
      }

      const newCategory = await response.json();
      categories.value.push(newCategory);
      
      // Sort categories by position
      categories.value.sort((a, b) => a.position - b.position);
      
      return newCategory;
    } catch (err: any) {
      error.value = err.message || 'Failed to create category';
      console.error('Error creating category:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const updateCategory = async (categoryId: number, categoryData: CategoryUpdate): Promise<Category | null> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/categories/${categoryId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(categoryData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to update category: ${response.statusText}`);
      }

      const updatedCategory = await response.json();
      
      // Update category in store
      const index = categories.value.findIndex(cat => cat.id === categoryId);
      if (index !== -1) {
        categories.value[index] = updatedCategory;
      }
      
      // Update current category if it's the one being updated
      if (currentCategory.value?.id === categoryId) {
        currentCategory.value = updatedCategory;
      }
      
      return updatedCategory;
    } catch (err: any) {
      error.value = err.message || 'Failed to update category';
      console.error('Error updating category:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const deleteCategory = async (categoryId: number): Promise<boolean> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/categories/${categoryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to delete category: ${response.statusText}`);
      }

      // Remove category from store (or mark as archived)
      const index = categories.value.findIndex(cat => cat.id === categoryId);
      if (index !== -1) {
        categories.value[index].is_archived = true;
      }
      
      // Clear current category if it's the one being deleted
      if (currentCategory.value?.id === categoryId) {
        currentCategory.value = null;
      }
      
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to delete category';
      console.error('Error deleting category:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const updateCategoryPosition = async (categoryId: number, newPosition: number): Promise<boolean> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/categories/${categoryId}/position`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ position: newPosition }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to update category position: ${response.statusText}`);
      }

      // Refresh categories to get updated positions
      const category = categories.value.find(cat => cat.id === categoryId);
      if (category) {
        await fetchWorkspaceCategories(category.workspace_id);
      }
      
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to update category position';
      console.error('Error updating category position:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const reorderCategories = async (workspaceId: number, categoryIds: number[]): Promise<boolean> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      // Update positions for all categories
      const updatePromises = categoryIds.map((categoryId, index) => 
        updateCategoryPosition(categoryId, index + 1)
      );

      await Promise.all(updatePromises);
      
      // Refresh categories to ensure consistency
      await fetchWorkspaceCategories(workspaceId);
      
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to reorder categories';
      console.error('Error reordering categories:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const getCategory = async (categoryId: number): Promise<Category | null> => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`/api/categories/${categoryId}`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to fetch category: ${response.statusText}`);
      }

      const category = await response.json();
      currentCategory.value = category;
      
      // Update category in store if it exists
      const index = categories.value.findIndex(cat => cat.id === categoryId);
      if (index !== -1) {
        categories.value[index] = category;
      } else {
        categories.value.push(category);
      }
      
      return category;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch category';
      console.error('Error fetching category:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  const clearCategories = () => {
    categories.value = [];
    currentCategory.value = null;
  };

  return {
    // State
    categories,
    loading,
    error,
    currentCategory,
    
    // Getters
    categoriesByWorkspace,
    getCategoryById,
    
    // Actions
    fetchWorkspaceCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    updateCategoryPosition,
    reorderCategories,
    getCategory,
    clearError,
    clearCategories,
  };
});