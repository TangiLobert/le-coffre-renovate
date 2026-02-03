<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue';
import CreateUserModal from '@/components/modals/CreateUserModal.vue';
import { listUsersUsersGet } from '@/client/sdk.gen';
import type { ListUserResponse } from '@/client/types.gen';

const toast = useToast();

// State
const users = ref<ListUserResponse[]>([]);
const loading = ref(false);
const showCreateUserModal = ref(false);

// Fetch users
const fetchUsers = async () => {
  loading.value = true;
  try {
    const response = await listUsersUsersGet();

    if (response.response.ok && response.data) {
      users.value = response.data;
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to fetch users',
        life: 5000
      });
    }
  } catch (error) {
    console.error('Failed to fetch users:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to fetch users',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

// Handle user created
const handleUserCreated = () => {
  fetchUsers();
};

onMounted(() => {
  fetchUsers();
});
</script>

<template>
  <Card>
    <template #title>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <i class="pi pi-users"></i>
          User Management
        </div>
        <Button label="Create User" icon="pi pi-user-plus" size="small" @click="showCreateUserModal = true" />
      </div>
    </template>
    <template #content>
      <p class="text-muted-color mb-4">
        Manage users and their access to the system.
      </p>

      <div v-if="loading" class="flex justify-center items-center py-8">
        <ProgressSpinner />
      </div>

      <div v-else-if="users.length === 0" class="text-center py-8">
        <i class="pi pi-users text-4xl text-muted-color mb-4"></i>
        <p class="text-muted-color">No users found. Create your first user!</p>
      </div>

      <DataTable v-else :value="users" stripedRows :paginator="users.length > 10" :rows="10"
        :rowsPerPageOptions="[10, 25, 50]" dataKey="id" responsiveLayout="scroll"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} users">

        <Column field="username" header="Username" sortable>
          <template #body="slotProps">
            <div class="flex items-center gap-2">
              <i class="pi pi-user text-muted-color"></i>
              <span class="font-semibold">{{ slotProps.data.username }}</span>
            </div>
          </template>
        </Column>

        <Column field="name" header="Name" sortable>
          <template #body="slotProps">
            <span>{{ slotProps.data.name }}</span>
          </template>
        </Column>

        <Column field="email" header="Email" sortable>
          <template #body="slotProps">
            <div class="flex items-center gap-2">
              <i class="pi pi-envelope text-muted-color text-sm"></i>
              <span>{{ slotProps.data.email }}</span>
            </div>
          </template>
        </Column>

        <Column field="id" header="User ID" sortable>
          <template #body="slotProps">
            <span class="font-mono text-sm text-muted-color">{{ slotProps.data.id }}</span>
          </template>
        </Column>
      </DataTable>

      <!-- Create User Modal -->
      <CreateUserModal v-model:visible="showCreateUserModal" @created="handleUserCreated" />
    </template>
  </Card>
</template>
