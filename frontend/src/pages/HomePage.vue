<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import MainLayout from "../layouts/MainLayout.vue";
import CreatePasswordModal from "@/components/CreatePasswordModal.vue";
import PasswordsList from "@/components/passwords/PasswordsList.vue";
import type { GetPasswordListResponse } from '@/client/types.gen';
import { listPasswordsPasswordsListGet } from '@/client';

const route = useRoute();
const passwords = ref<GetPasswordListResponse[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const selectedFolder = ref<string | null>(null);
const showCreateModal = ref(false);

const folderFilter = computed(() => route.query.folder as string | undefined);

const loadPasswords = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await listPasswordsPasswordsListGet();
    passwords.value = response.data ?? [];
    
    // Auto-expand folder if filtered
    const folderQuery = route.query.folder as string | undefined;
    if (folderQuery) {
      selectedFolder.value = folderQuery;
    }
  } catch (e) {
    console.error('Error loading passwords:', e);
    error.value = 'Failed to load passwords';
  } finally {
    loading.value = false;
  }
};

const handlePasswordCreated = async () => {
  // Reload the passwords list
  await loadPasswords();
};

// Watch for route changes to reload/filter
watch(() => route.query.folder, (folderQuery) => {
  selectedFolder.value = folderQuery as string | null;
});

onMounted(() => {
  loadPasswords();
});
</script>

<template>
  <MainLayout>
    <div class="container mx-auto p-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">Password Manager</h1>
        <Button label="New Password" icon="pi pi-plus" @click="showCreateModal = true" />
      </div>
      
      <PasswordsList 
        :passwords="passwords"
        :loading="loading"
        :error="error"
        :selectedFolder="selectedFolder"
        :folderFilter="folderFilter"
      />
    </div>
    
    <!-- Create Password Modal -->
    <CreatePasswordModal v-model:visible="showCreateModal" @created="handlePasswordCreated" />
  </MainLayout>
</template>
