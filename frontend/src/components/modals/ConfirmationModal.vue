<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue';

defineOptions({
  inheritAttrs: false
});

const visible = defineModel<boolean>('visible', { required: true });

const props = withDefaults(defineProps<{
  title: string;
  question: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  severity?: 'danger' | 'warning' | 'info' | 'success';
  icon?: string;
  countdownSeconds?: number;
  warningMessage?: string;
  canProceed?: boolean;
}>(), {
  canProceed: undefined
});

const emit = defineEmits<{
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();

const countdown = ref(0);
const isProcessing = ref(false);
const countdownTimer = ref<number | null>(null);

// Debug: Log initial canProceed value and create unique ID for this instance
const instanceId = Math.random().toString(36).substring(7);
console.log(`ConfirmationModal [${instanceId}] created with:`, {
  title: props.title,
  canProceed: props.canProceed,
  type: typeof props.canProceed,
  countdownSeconds: props.countdownSeconds
});

const canConfirm = computed(() => {
  // Enable when countdown reaches 0
  const countdownDone = countdown.value === 0;
  
  // Only block if canProceed is explicitly false AND we're not just doing a countdown
  // If canProceed is undefined or true, rely on countdown
  const canProceedCheck = props.canProceed === undefined || props.canProceed === true;
  
  const result = countdownDone && canProceedCheck;
  
  console.log('canConfirm computed:', {
    canProceed: props.canProceed,
    canProceedType: typeof props.canProceed,
    canProceedIsUndefined: props.canProceed === undefined,
    countdown: countdown.value,
    countdownDone,
    canProceedCheck,
    result
  });
  return result;
});

// Compute button label based on countdown
const confirmButtonLabel = computed(() => {
  if (countdown.value > 0) {
    return `${props.confirmLabel || 'Confirm'} in ${countdown.value}s`;
  }
  return props.confirmLabel || 'Confirm';
});

// Get icon based on severity
const iconClass = computed(() => {
  if (props.icon) return props.icon;

  switch (props.severity) {
    case 'danger':
      return 'pi pi-exclamation-triangle';
    case 'warning':
      return 'pi pi-exclamation-circle';
    case 'info':
      return 'pi pi-info-circle';
    case 'success':
      return 'pi pi-check-circle';
    default:
      return 'pi pi-question-circle';
  }
});

const iconColor = computed(() => {
  switch (props.severity) {
    case 'danger':
      return 'text-red-500';
    case 'warning':
      return 'text-yellow-500';
    case 'info':
      return 'text-blue-500';
    case 'success':
      return 'text-green-500';
    default:
      return 'text-muted-color';
  }
});

// Start countdown when modal opens
watch(visible, async (newVisible) => {
  console.log('ConfirmationModal visible changed:', newVisible, 'countdownSeconds:', props.countdownSeconds);
  if (newVisible) {
    // Reset countdown when modal opens
    countdown.value = props.countdownSeconds || 0;
    isProcessing.value = false; // Reset processing state
    console.log('Set countdown to:', countdown.value);

    // Use nextTick to ensure reactivity is complete
    await nextTick();

    if (countdown.value > 0) {
      console.log('Starting countdown...');
      startCountdown();
    }
  } else {
    stopCountdown();
    isProcessing.value = false; // Reset when modal closes
  }
});

const startCountdown = () => {
  stopCountdown(); // Clear any existing timer
  countdownTimer.value = window.setInterval(() => {
    console.log('Countdown tick:', countdown.value);
    if (countdown.value > 0) {
      countdown.value--;
    } else {
      console.log('Countdown finished, stopping timer');
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

const handleConfirm = () => {
  emit('confirm');
  visible.value = false;
};

const handleCancel = () => {
  emit('cancel');
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
  <Dialog v-model:visible="visible" :header="title" :modal="true" :closable="!isProcessing" :style="{ width: '30rem' }">
    <div class="flex flex-col gap-4 py-4">
      <div class="flex items-start gap-3">
        <i :class="[iconClass, iconColor, 'text-2xl']"></i>
        <div class="flex-1">
          <!-- Question (bold) -->
          <p class="font-semibold mb-3">
            {{ question }}
          </p>

          <!-- Description (multiple lines) -->
          <div class="text-sm text-muted-color mb-3 space-y-1">
            <p v-for="(line, index) in description.split('\n')" :key="index">
              {{ line }}
            </p>
          </div>

          <!-- Warning message -->
          <div v-if="warningMessage"
            class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded p-3 mb-3">
            <p class="text-sm text-yellow-800 dark:text-yellow-200">
              <i class="pi pi-exclamation-triangle mr-2"></i>
              {{ warningMessage }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <Button :label="cancelLabel || 'Cancel'" icon="pi pi-times" text @click="handleCancel" :disabled="isProcessing" />
      <Button :label="confirmButtonLabel" icon="pi pi-check" :severity="severity || 'primary'" @click="handleConfirm"
        :disabled="!canConfirm || isProcessing" :loading="isProcessing" />
    </template>
  </Dialog>
</template>
