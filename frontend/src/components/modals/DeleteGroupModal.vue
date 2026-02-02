<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import type { GroupItem } from '@/client/types.gen';

const visible = defineModel<boolean>('visible', { required: true });

const props = defineProps<{
  group?: GroupItem | null;
  canDelete: boolean;
  hasPasswords: boolean;
}>();

const emit = defineEmits<{
  (e: 'deleted'): void;
}>();

const countdown = ref(6);
const isDeleting = ref(false);
const countdownTimer = ref<number | null>(null);

const canProceed = computed(() => countdown.value === 0 && props.canDelete);

// Compute button label based on countdown
const deleteButtonLabel = computed(() => {
  if (countdown.value > 0) {
    return `Delete group in ${countdown.value}s`;
  }
  return 'Delete Group';
});

// Start countdown when modal opens
watch(visible, (newVisible) => {
  if (newVisible) {
    countdown.value = 6;
    startCountdown();
  } else {
    stopCountdown();
  }
});

const startCountdown = () => {
  stopCountdown(); // Clear any existing timer
  countdownTimer.value = window.setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--;
    } else {
      stopCountdown();
    }
  }, 1000);
};

const stopCountdown = () => {
  if (countdownTimer.value !== null) {
    clearInterval(countdownTimer.value);
    countdownTimer.value = null;
  }
};

const handleDelete = () => {
  emit('deleted');
  visible.value = false;
};

const handleCancel = () => {
  visible.value = false;
};

// Clean up timer when component unmounts
watch(() => visible.value, (newVal) => {
  if (!newVal) {
    stopCountdown();
  }
});
</script>

<template>
  <Dialog v-model:visible="visible" header="Delete Group" :modal="true" :closable="!isDeleting"
    :style="{ width: '30rem' }">
    <div class="flex flex-col gap-4 py-4">
      <div class="flex items-start gap-3">
        <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
        <div class="flex-1">
          <p class="font-semibold mb-2">
            Are you sure you want to delete "{{ group?.name }}"?
          </p>

          <div v-if="!canDelete && hasPasswords"
            class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-3 mb-3">
            <p class="text-sm text-red-800 dark:text-red-200">
              <i class="pi pi-ban mr-2"></i>
              This group contains passwords and cannot be deleted. Please remove or reassign all passwords before
              deleting this group.
            </p>
          </div>

          <div v-else-if="!canDelete"
            class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded p-3 mb-3">
            <p class="text-sm text-yellow-800 dark:text-yellow-200">
              <i class="pi pi-lock mr-2"></i>
              You don't have permission to delete this group. Only admins and group owners can delete groups.
            </p>
          </div>

          <div v-else>
            <p class="text-sm text-muted-color mb-2">
              This action cannot be undone. All group members will lose access.
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" icon="pi pi-times" text @click="handleCancel" :disabled="isDeleting" />
      <Button :label="deleteButtonLabel" icon="pi pi-trash" severity="danger" @click="handleDelete"
        :disabled="!canProceed || isDeleting" :loading="isDeleting" />
    </template>
  </Dialog>
</template>
