<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import MainLayout from '../layouts/MainLayout.vue';
import { getUserMeUsersMeGet, updateUserPasswordUsersMePasswordPut } from '@/client/sdk.gen';
import type { GetUserMeResponse } from '@/client';

const toast = useToast();

const user = ref<GetUserMeResponse | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

// Password update
const showPasswordDialog = ref(false);
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});
const passwordLoading = ref(false);

const fetchUserInfo = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await getUserMeUsersMeGet();
    if (response.data) {
      user.value = response.data;
    }
  } catch (err) {
    error.value = 'Erreur lors du chargement des informations utilisateur';
    console.error('Error fetching user info:', err);
  } finally {
    loading.value = false;
  }
};

const resetPasswordForm = () => {
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
};

const updatePassword = async () => {
  // Validation
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    toast.add({
      severity: 'error',
      summary: 'Erreur',
      detail: 'Tous les champs sont requis',
      life: 3000
    });
    return;
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    toast.add({
      severity: 'error',
      summary: 'Erreur',
      detail: 'Les mots de passe ne correspondent pas',
      life: 3000
    });
    return;
  }

  if (passwordForm.value.newPassword.length < 8) {
    toast.add({
      severity: 'error',
      summary: 'Erreur',
      detail: 'Le nouveau mot de passe doit contenir au moins 8 caractères',
      life: 3000
    });
    return;
  }

  try {
    passwordLoading.value = true;
    const response = await updateUserPasswordUsersMePasswordPut({
      body: {
        old_password: passwordForm.value.oldPassword,
        new_password: passwordForm.value.newPassword
      }
    });

    if (response.error) {
      const errorData = response.error as { detail?: string };
      const errorMessage = errorData?.detail || 'Erreur lors de la mise à jour du mot de passe';
      toast.add({
        severity: 'error',
        summary: 'Erreur',
        detail: errorMessage,
        life: 3000
      });
      return;
    }

    toast.add({
      severity: 'success',
      summary: 'Succès',
      detail: 'Mot de passe mis à jour avec succès',
      life: 3000
    });

    showPasswordDialog.value = false;
    resetPasswordForm();
  } catch (err: unknown) {
    console.error('Error updating password:', err);
    toast.add({
      severity: 'error',
      summary: 'Erreur',
      detail: 'Une erreur inattendue est survenue',
      life: 3000
    });
  } finally {
    passwordLoading.value = false;
  }
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<template>
  <MainLayout>
    <Toast />
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-6">Profil</h1>

      <!-- Loading state -->
      <div v-if="loading" class="rounded-lg p-6 text-center">
        <ProgressSpinner />
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="surface-ground border border-red-500 rounded-lg p-6">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <!-- User info -->
      <div v-else-if="user" class="rounded-lg p-6 space-y-4">
        <div class="border-b pb-4">
          <h2 class="text-xl font-semibold">
            Display Name: {{ user.name }}
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium mb-1">
              Nom d'utilisateur
            </label>
            <p>{{ user.username }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">
              Email
            </label>
            <p>{{ user.email }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">
              ID
            </label>
            <p class="font-mono text-sm">{{ user.id }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">
              Rôles
            </label>
            <div class="flex flex-wrap gap-2">
              <span v-for="role in user.roles" :key="role"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                {{ role }}
              </span>
            </div>
          </div>
        </div>

        <!-- Password Update Section -->
        <div class="border-t pt-4 mt-6">
          <h3 class="text-lg font-semibold mb-4">Sécurité</h3>
          <Button label="Changer mon mot de passe" icon="pi pi-key" @click="showPasswordDialog = true"
            class="p-button-outlined" />
        </div>
      </div>

      <!-- Password Update Dialog -->
      <Dialog v-model:visible="showPasswordDialog" header="Changer mon mot de passe" :modal="true" :closable="true"
        :style="{ width: '450px' }" @hide="resetPasswordForm">
        <div class="space-y-4">
          <div>
            <label for="oldPassword" class="block text-sm font-medium mb-2">
              Mot de passe actuel
            </label>
            <Password id="oldPassword" v-model="passwordForm.oldPassword" :feedback="false" toggleMask
              placeholder="Entrez votre mot de passe actuel" class="w-full" inputClass="w-full" />
          </div>

          <div>
            <label for="newPassword" class="block text-sm font-medium mb-2">
              Nouveau mot de passe
            </label>
            <Password id="newPassword" v-model="passwordForm.newPassword" toggleMask
              placeholder="Entrez votre nouveau mot de passe" class="w-full" inputClass="w-full" />
            <small class="text-muted-color">Minimum 8 caractères</small>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium mb-2">
              Confirmer le nouveau mot de passe
            </label>
            <Password id="confirmPassword" v-model="passwordForm.confirmPassword" :feedback="false" toggleMask
              placeholder="Confirmez votre nouveau mot de passe" class="w-full" inputClass="w-full" />
          </div>
        </div>

        <template #footer>
          <Button label="Annuler" icon="pi pi-times" @click="showPasswordDialog = false" class="p-button-text"
            :disabled="passwordLoading" />
          <Button label="Mettre à jour" icon="pi pi-check" @click="updatePassword" :loading="passwordLoading" />
        </template>
      </Dialog>
    </div>
  </MainLayout>
</template>
