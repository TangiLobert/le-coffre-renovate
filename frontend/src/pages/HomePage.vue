<script setup lang="ts">
import MainLayout from '../layouts/MainLayout.vue'
import PasswordsList from '@/components/passwords/PasswordsList.vue'
</script>

<template>
  <MainLayout>
    <div class="container mx-auto p-6">
      <PasswordsList />
    </div>
  </MainLayout>
</template>
