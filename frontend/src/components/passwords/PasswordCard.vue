<template>
  <div
    class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
  >
    <div class="flex justify-between items-start">
      <div class="flex-1">
        <h4 class="font-semibold mb-2">{{ password.name }}</h4>
        <div class="flex items-center gap-2">
          <code class="text-sm bg-white dark:bg-gray-900 px-3 py-1 rounded border border-gray-200 dark:border-gray-600">
            ••••••••
          </code>
          <Button 
            icon="pi pi-eye" 
            text 
            rounded 
            size="small"
            severity="secondary"
            aria-label="Show password"
          />
          <Button 
            icon="pi pi-copy" 
            text 
            rounded 
            size="small"
            severity="secondary"
            aria-label="Copy password"
          />
        </div>
      </div>
      <div class="flex gap-1">
        <Button 
          icon="pi pi-pencil" 
          text 
          rounded 
          size="small"
          severity="secondary"
          aria-label="Edit"
        />
        <Button 
          icon="pi pi-trash" 
          text 
          rounded 
          size="small"
          severity="danger"
          aria-label="Delete"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GetPasswordListResponse } from '@/client/types.gen';

defineProps<{
  password: GetPasswordListResponse;
}>();
</script>
