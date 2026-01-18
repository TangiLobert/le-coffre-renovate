<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { storeToRefs } from 'pinia';
import { 
  sharePasswordPasswordsPasswordIdSharePost, 
  listPasswordAccessPasswordsPasswordIdAccessGet 
} from '@/client/sdk.gen';
import type { GetPasswordListResponse, UserAccessItem } from '@/client/types.gen';
import { useGroupsStore } from '@/stores/groups';

const visible = defineModel<boolean>('visible', { required: true });

const props = defineProps<{
  password?: GetPasswordListResponse | null;
}>();

const emit = defineEmits<{
  (e: 'shared'): void;
  (e: 'unshared'): void;
}>();

const toast = useToast();
const groupsStore = useGroupsStore();
const { sharedGroups } = storeToRefs(groupsStore);

const selectedGroupId = ref<string>('');
const loading = ref(false);
const loadingAccess = ref(false);
const accessList = ref<UserAccessItem[]>([]);
const isOwner = ref(false);

// Get current user ID from store
const currentUserId = computed(() => groupsStore.currentUserId);

// Get groups that can be shared with (excluding owner's personal group)
const availableGroupsForSharing = computed(() => {
  // Show all shared groups for now
  // Future: Could filter out groups that already have access
  return sharedGroups.value;
});

// Load password access list to determine if user is owner
const loadAccessList = async () => {
  if (!props.password) return;
  
  loadingAccess.value = true;
  try {
    const response = await listPasswordAccessPasswordsPasswordIdAccessGet({
      path: { password_id: props.password.id }
    });
    
    if (response.data) {
      accessList.value = response.data.access_list;
      // Check if current user is the owner
      const currentUserAccess = accessList.value.find(
        item => item.user_id === currentUserId.value
      );
      isOwner.value = currentUserAccess?.is_owner ?? false;
    }
  } catch (error) {
    console.error('Error loading access list:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load sharing information',
      life: 5000
    });
  } finally {
    loadingAccess.value = false;
  }
};

// Watch for password changes
watch(() => props.password, async (newPassword) => {
  if (newPassword && visible.value) {
    await loadAccessList();
  }
}, { immediate: true });

// Watch for modal visibility
watch(visible, async (isVisible) => {
  if (isVisible && props.password) {
    await loadAccessList();
    selectedGroupId.value = '';
  }
});

// Share password with group
const sharePassword = async () => {
  if (!props.password || !selectedGroupId.value) {
    toast.add({
      severity: 'error',
      summary: 'Validation Error',
      detail: 'Please select a group',
      life: 5000
    });
    return;
  }

  if (!isOwner.value) {
    toast.add({
      severity: 'error',
      summary: 'Permission Denied',
      detail: 'Only the owner can share this password',
      life: 5000
    });
    return;
  }

  loading.value = true;
  try {
    await sharePasswordPasswordsPasswordIdSharePost({
      path: { password_id: props.password.id },
      body: { group_id: selectedGroupId.value }
    });

    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Password shared successfully',
      life: 5000
    });

    selectedGroupId.value = '';
    await loadAccessList();
    emit('shared');
  } catch (error) {
    console.error('Error sharing password:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to share password',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await groupsStore.fetchAllGroups();
});
</script>

<template>
  <Dialog 
    v-model:visible="visible" 
    modal 
    header="Share Password" 
    :style="{ width: '36rem' }"
  >
    <div v-if="!isOwner && !loadingAccess" class="mb-4">
      <Message severity="warn" :closable="false">
        You are not the owner of this password. Only the owner can manage sharing.
      </Message>
    </div>

    <div v-if="loadingAccess" class="flex justify-center py-4">
      <ProgressSpinner />
    </div>

    <div v-else class="flex flex-col gap-4">
      <!-- Share with new group -->
      <div v-if="isOwner" class="flex flex-col gap-4 pb-4 border-b">
        <h3 class="font-semibold text-lg">Share with Group</h3>
        <div class="flex gap-2">
          <Select 
            id="group-select"
            v-model="selectedGroupId" 
            :options="availableGroupsForSharing"
            optionLabel="name"
            optionValue="id"
            placeholder="Select a group to share with"
            :disabled="loading"
            class="flex-1"
          >
            <template #option="slotProps">
              <div class="flex items-center gap-2">
                <i class="pi pi-users text-sm"></i>
                <span>{{ slotProps.option.name }}</span>
              </div>
            </template>
          </Select>
          <Button 
            label="Share" 
            icon="pi pi-share-alt"
            @click="sharePassword"
            :loading="loading"
            :disabled="!selectedGroupId || loading"
          />
        </div>
      </div>

      <!-- Current access list -->
      <div class="flex flex-col gap-3">
        <h3 class="font-semibold text-lg">Who has access</h3>
        
        <div v-if="accessList.length === 0" class="text-center py-4 text-muted-color">
          <p>No users have access yet</p>
        </div>

        <div v-else class="space-y-2">
          <Card 
            v-for="accessItem in accessList" 
            :key="accessItem.user_id"
            class="hover:bg-surface-50 transition-colors"
          >
            <template #content>
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-3">
                  <i class="pi pi-user text-xl text-primary"></i>
                  <div>
                    <p class="font-semibold">User ID: {{ accessItem.user_id.substring(0, 8) }}...</p>
                    <div class="flex gap-2 items-center text-sm text-muted-color">
                      <span v-if="accessItem.is_owner" class="flex items-center gap-1">
                        <i class="pi pi-crown text-yellow-500"></i>
                        Owner
                      </span>
                      <span v-else class="flex items-center gap-1">
                        <i class="pi pi-eye"></i>
                        Can read
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- Note: We can't unshare by user_id anymore, need to implement group-based unsharing -->
                <!-- This would require fetching group membership information -->
                <div v-if="isOwner && !accessItem.is_owner">
                  <Button 
                    icon="pi pi-times"
                    text
                    rounded
                    severity="danger"
                    size="small"
                    aria-label="Remove access"
                    :loading="loading"
                    disabled
                    v-tooltip="'Group-based unsharing - feature coming soon'"
                  />
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>
    </div>

    <template #footer>
      <Button 
        label="Close" 
        severity="secondary" 
        @click="visible = false" 
        :disabled="loading" 
      />
    </template>
  </Dialog>
</template>
