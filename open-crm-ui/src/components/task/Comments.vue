<template>
    <v-card class="mt-4">
        <v-card-title class="d-flex justify-space-between align-center">
            <span>Comments</span>
            <v-btn icon="mdi-plus" @click="showAddComment = true" color="primary"></v-btn>
        </v-card-title>

        <v-card-text>
            <v-progress-circular v-if="loading" indeterminate color="primary" class="ma-4"></v-progress-circular>

            <div v-else-if="comments && comments.length > 0">
                <v-card v-for="comment in comments" :key="comment.id" class="mb-3 comment-card" elevation="1">
                    <v-card-title class="py-2 d-flex justify-space-between align-center">
                        <span class="font-weight-bold primary--text">{{ comment.createdBy }}</span>

                        <div class="d-flex align-center">
                            <span class="text-caption text-grey mr-2">{{ formatDate(comment.createdAt) }}</span>

                            <v-menu>
                                <template v-slot:activator="{ props }">
                                    <v-btn icon="mdi-dots-vertical" variant="text" density="compact"
                                        v-bind="props"></v-btn>
                                </template>
                                <v-list>
                                    <v-list-item @click="replyToComment(comment)">
                                        <v-list-item-title>Reply</v-list-item-title>
                                    </v-list-item>
                                    <v-list-item @click="editComment(comment)">
                                        <v-list-item-title>Edit</v-list-item-title>
                                    </v-list-item>
                                </v-list>
                            </v-menu>
                        </div>
                    </v-card-title>

                    <v-card-text class="py-2 grey lighten-4">
                        {{ comment.content }}
                    </v-card-text>

                    <!-- Nested replies -->
                    <div v-if="comment.replies && comment.replies.length > 0" class="pl-6">
                        <v-card v-for="reply in comment.replies" :key="reply.id" class="mb-2 ml-6 reply-card"
                            elevation="0" outlined>
                            <v-card-title class="py-1 d-flex justify-space-between">
                                <span class="font-weight-bold primary--text text-subtitle-2">{{ reply.createdBy
                                }}</span>
                                <span class="text-caption text-grey">{{ formatDate(reply.createdAt) }}</span>
                            </v-card-title>
                            <v-card-text class="py-1 grey lighten-5">
                                {{ reply.content }}
                            </v-card-text>
                        </v-card>
                    </div>
                </v-card>
            </div>
            <div v-else class="text-center py-4">
                <v-icon size="48" color="grey lighten-1">mdi-comment-outline</v-icon>
                <div class="text-h6 text-grey mt-2">No comments yet</div>
                <div class="text-body-2 text-grey">Be the first to add a comment</div>
            </div>
        </v-card-text>

        <!-- Add Comment Dialog -->
        <v-dialog v-model="showAddComment" max-width="500">
            <v-card>
                <v-card-title>
                    {{ replyingTo ? 'Reply to Comment' : 'Add Comment' }}
                </v-card-title>
                <v-card-text>
                    <v-textarea v-model="newCommentText"
                        :label="replyingTo ? `Reply to ${replyingTo.createdBy}` : 'Comment'" counter auto-grow
                        rows="3"></v-textarea>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="grey" variant="text" @click="cancelComment">
                        Cancel
                    </v-btn>
                    <v-btn color="primary" @click="submitComment" :disabled="!newCommentText.trim()">
                        {{ replyingTo ? 'Reply' : 'Add' }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Edit Comment Dialog -->
        <v-dialog v-model="showEditDialog" max-width="500">
            <v-card>
                <v-card-title>
                    Edit Comment
                </v-card-title>
                <v-card-text>
                    <v-textarea v-model="editCommentText" label="Edit your comment" counter auto-grow
                        rows="3"></v-textarea>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="grey" variant="text" @click="showEditDialog = false">
                        Cancel
                    </v-btn>
                    <v-btn color="primary" @click="updateComment" :disabled="!editCommentText.trim()">
                        Update
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTaskStore } from '@/stores/tasks'
import { useAuthStore } from '@/stores/auth'

interface Comment {
    id: number;
    content: string;
    createdBy: string;
    createdAt: string;
    parentCommentId?: number;
    replies?: Comment[];
}

const props = defineProps<{
    taskId: string;
}>()

const emit = defineEmits(['comment-added'])

const taskStore = useTaskStore()
const authStore = useAuthStore()
const showAddComment = ref(false)
const showEditDialog = ref(false)
const newCommentText = ref('')
const editCommentText = ref('')
const replyingTo = ref<Comment | null>(null)
const editingComment = ref<Comment | null>(null)
const comments = ref<Comment[]>([])
const loading = ref(false)

async function fetchComments() {
    loading.value = true
    try {
        comments.value = await taskStore.getTaskComments(props.taskId)
    } catch (error) {
        console.error('Error fetching comments:', error)
    } finally {
        loading.value = false
    }
}

function formatDate(dateString: string) {
    if (!dateString) return ''
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date)
}

function replyToComment(comment: Comment) {
    replyingTo.value = comment
    newCommentText.value = ''
    showAddComment.value = true
}

function editComment(comment: Comment) {
    // Only allow editing if comment created by current user
    if (comment.createdBy !== authStore.username) {
        return
    }

    editingComment.value = comment
    editCommentText.value = comment.content
    showEditDialog.value = true
}

function cancelComment() {
    replyingTo.value = null
    newCommentText.value = ''
    showAddComment.value = false
}

async function submitComment() {
    if (newCommentText.value.trim() === '') return

    try {
        const payload = {
            content: newCommentText.value,
            createdBy: authStore.username,
        }

        if (replyingTo.value) {
            payload.parentCommentId = replyingTo.value.id
        }

        await taskStore.addComment(props.taskId, newCommentText.value, replyingTo.value?.id)
        await fetchComments() // Refresh comments

        newCommentText.value = ''
        replyingTo.value = null
        showAddComment.value = false
        emit('comment-added')
    } catch (error) {
        console.error('Error adding comment:', error)
    }
}

async function updateComment() {
    if (!editingComment.value || editCommentText.value.trim() === '') return

    try {
        await taskStore.updateComment(
            props.taskId,
            editingComment.value.id,
            editCommentText.value
        )

        await fetchComments() // Refresh comments

        editCommentText.value = ''
        editingComment.value = null
        showEditDialog.value = false
        emit('comment-added')
    } catch (error) {
        console.error('Error updating comment:', error)
    }
}

onMounted(fetchComments)
</script>

<style scoped>
.comment-card {
    border-left: 3px solid var(--v-primary-base);
}

.reply-card {
    border-left: 2px solid var(--v-secondary-base);
}
</style>