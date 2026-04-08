<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import type { GetPasswordListResponse, GroupItem } from '@/client/types.gen'
import FolderCard from './FolderCard.vue'
import CreatePasswordModal from '@/components/modals/CreatePasswordModal.vue'
import SharePasswordModal from '@/components/modals/SharePasswordModal.vue'
import PasswordHistoryModal from '@/components/modals/PasswordHistoryModal.vue'
import { listPasswordAccessPasswordsPasswordIdAccessGet } from '@/client/sdk.gen'
import { usePasswordsStore } from '@/stores/passwords'
import { useGroupsStore } from '@/stores/groups'
import { useUserStore } from '@/stores/user'
import { sortGroupsByName } from '@/utils/groupSort'

const route = useRoute()
const passwordsStore = usePasswordsStore()
const groupsStore = useGroupsStore()
const userStore = useUserStore()

const { passwords, loading, error } = storeToRefs(passwordsStore)
const { groups, userBelongingGroups, currentUserPersonalGroupId } = storeToRefs(groupsStore)
const { isAdmin, currentUser } = storeToRefs(userStore)

const openFolderKey = ref<string | null>(null)
const selectedGroupTabId = ref<string | null>(null)

// Modal state
const showCreateModal = ref(false)
const showShareModal = ref(false)
const showHistoryModal = ref(false)
const defaultCreateGroupId = ref<string | null>(null)
const editingPassword = ref<GetPasswordListResponse | null>(null)
const sharingPassword = ref<GetPasswordListResponse | null>(null)
const historyPassword = ref<GetPasswordListResponse | null>(null)

// Filter state
const searchQuery = ref('')
const adminViewEnabled = ref(false)
const passwordAccessibleGroupIds = ref<Record<string, string[]>>({})
let accessMapLoadVersion = 0

const filterableGroups = computed(() => {
  if (!isAdmin.value) {
    return userBelongingGroups.value
  }

  if (!adminViewEnabled.value) {
    return userBelongingGroups.value
  }

  return groups.value
})

const getAccessibleGroupIdsForPassword = (password: GetPasswordListResponse): string[] =>
  passwordAccessibleGroupIds.value[password.id] ?? [password.group_id]

const loadPasswordAccessibleGroupIds = async () => {
  const currentVersion = ++accessMapLoadVersion

  if (passwords.value.length === 0) {
    passwordAccessibleGroupIds.value = {}
    return
  }

  const entries = await Promise.all(
    passwords.value.map(async (password) => {
      try {
        const response = await listPasswordAccessPasswordsPasswordIdAccessGet({
          path: { password_id: password.id },
        })

        const groupIds = [
          ...new Set((response.data?.group_access_list ?? []).map((item) => item.user_id)),
        ]
        return [password.id, groupIds.length > 0 ? groupIds : [password.group_id]] as const
      } catch {
        return [password.id, [password.group_id]] as const
      }
    }),
  )

  if (currentVersion !== accessMapLoadVersion) {
    return
  }

  passwordAccessibleGroupIds.value = Object.fromEntries(entries)
}

const matchesSearchQuery = (password: GetPasswordListResponse, groupName?: string): boolean => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return true

  return (
    (groupName?.toLowerCase().includes(q) ?? false) ||
    password.folder.toLowerCase().includes(q) ||
    (password.name?.toLowerCase().includes(q) ?? false) ||
    (password.login?.toLowerCase().includes(q) ?? false) ||
    (password.url?.toLowerCase().includes(q) ?? false)
  )
}

const folderFilter = computed(() => route.query.folder as string | undefined)
type GroupedFolder = {
  name: string
  count: number
  passwords: GetPasswordListResponse[]
}

type GroupedSection = {
  id: string
  name: string
  isPersonal: boolean
  isOwnedByCurrentUser: boolean
  count: number
  folders: GroupedFolder[]
}

const groupedByGroupAndFolder = computed<GroupedSection[]>(() => {
  const sortedVisibleGroups = sortGroupsByName(
    filterableGroups.value,
    currentUserPersonalGroupId.value,
  )
  const groupsById = new Map<string, GroupItem>(sortedVisibleGroups.map((g) => [g.id, g]))
  const currentUserId = currentUser.value?.id
  const visibleGroupIds = new Set(sortedVisibleGroups.map((g) => g.id))

  const groupPasswordMap = new Map<string, GetPasswordListResponse[]>()

  for (const password of passwords.value) {
    const accessibleGroupIds = getAccessibleGroupIdsForPassword(password)
    for (const groupId of accessibleGroupIds) {
      if (!visibleGroupIds.has(groupId)) continue
      const groupName = groupsById.get(groupId)?.name
      if (!matchesSearchQuery(password, groupName)) continue
      if (!groupPasswordMap.has(groupId)) groupPasswordMap.set(groupId, [])
      groupPasswordMap.get(groupId)!.push(password)
    }
  }

  const orderedGroupIds = sortedVisibleGroups.map((g) => g.id)

  const sections: GroupedSection[] = []

  for (const groupId of orderedGroupIds) {
    const groupPasswords = groupPasswordMap.get(groupId)
    if (!groupPasswords || groupPasswords.length === 0) continue

    const folderMap = new Map<string, GetPasswordListResponse[]>()
    for (const password of groupPasswords) {
      const folderName = password.folder
      if (!folderMap.has(folderName)) folderMap.set(folderName, [])
      folderMap.get(folderName)!.push(password)
    }

    const folders = Array.from(folderMap.entries())
      .filter(([folderName]) => !folderFilter.value || folderName === folderFilter.value)
      .map(([name, items]) => ({
        name,
        count: items.length,
        passwords: items,
      }))

    if (folders.length === 0) continue

    const group = groupsById.get(groupId)
    const isOwnedByCurrentUser = !!(group && currentUserId && group.owners?.includes(currentUserId))

    sections.push({
      id: groupId,
      name: group?.name ?? groupId,
      isPersonal: group?.is_personal ?? false,
      isOwnedByCurrentUser,
      count: groupPasswords.length,
      folders,
    })
  }

  return sections
})

// Handlers
const handlePasswordCreated = async () => {
  await passwordsStore.refresh()
}

const handlePasswordUpdated = async () => {
  await passwordsStore.refresh()
}

const handleCreateInGroup = (groupId: string) => {
  editingPassword.value = null
  defaultCreateGroupId.value = groupId
  showCreateModal.value = true
}

const handleEdit = (password: GetPasswordListResponse) => {
  defaultCreateGroupId.value = null
  editingPassword.value = password
  showCreateModal.value = true
}

const handleShare = (password: GetPasswordListResponse) => {
  sharingPassword.value = password
  showShareModal.value = true
}

const handleHistory = (password: GetPasswordListResponse) => {
  historyPassword.value = password
  showHistoryModal.value = true
}

const handleDeleted = async () => {
  await passwordsStore.refresh()
}

const handleShared = async () => {
  await passwordsStore.refresh()
}

const handleUnshared = async () => {
  await passwordsStore.refresh()
}

const handleFolderToggle = (folderKey: string) => {
  openFolderKey.value = openFolderKey.value === folderKey ? null : folderKey
}

const handleSelectGroupTab = (groupId: string) => {
  if (selectedGroupTabId.value === groupId) {
    return
  }

  selectedGroupTabId.value = groupId
  openFolderKey.value = null
}

const selectedGroupSection = computed(() => {
  if (!selectedGroupTabId.value) return null
  return (
    groupedByGroupAndFolder.value.find((section) => section.id === selectedGroupTabId.value) ?? null
  )
})

const handleAdminView = async () => {
  if (!isAdmin.value) return

  adminViewEnabled.value = !adminViewEnabled.value
  selectedGroupTabId.value = null
  openFolderKey.value = null
}

watch(groupedByGroupAndFolder, (sections) => {
  if (sections.length === 0) {
    selectedGroupTabId.value = null
    openFolderKey.value = null
    return
  }

  if (
    !selectedGroupTabId.value ||
    !sections.some((section) => section.id === selectedGroupTabId.value)
  ) {
    selectedGroupTabId.value = sections[0].id
    openFolderKey.value = null
  }
})

// Reset editing state when modals close
watch(showCreateModal, (isVisible) => {
  if (!isVisible) {
    editingPassword.value = null
    defaultCreateGroupId.value = null
  }
})
watch(showShareModal, (isVisible) => {
  if (!isVisible) sharingPassword.value = null
})
watch(showHistoryModal, (isVisible) => {
  if (!isVisible) historyPassword.value = null
})

watch(
  passwords,
  async () => {
    await loadPasswordAccessibleGroupIds()
  },
  { immediate: true },
)

onMounted(async () => {
  await Promise.all([passwordsStore.fetchPasswords(), groupsStore.fetchAllGroups()])
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Password Manager</h1>
      <Button label="New Password" icon="pi pi-plus" @click="showCreateModal = true" />
    </div>

    <!-- Filters row -->
    <div class="flex flex-wrap items-center gap-4 mb-4">
      <IconField>
        <InputIcon class="pi pi-search" />
        <InputText v-model="searchQuery" placeholder="Filter" class="min-w-64" />
      </IconField>

      <Button
        v-if="isAdmin"
        label="Admin view"
        :icon="adminViewEnabled ? 'pi pi-eye' : 'pi pi-eye-slash'"
        :severity="adminViewEnabled ? 'primary' : 'secondary'"
        :outlined="!adminViewEnabled"
        @click="handleAdminView"
      />
    </div>

    <!-- List -->
    <div v-if="loading" class="text-center py-8">
      <ProgressSpinner />
    </div>

    <div
      v-else-if="error"
      class="surface-ground border border-red-500 text-red-700 px-4 py-3 rounded mb-4"
    >
      {{ error }}
    </div>

    <div v-else-if="groupedByGroupAndFolder.length === 0" class="text-center py-8 text-surface-500">
      <p>No passwords to display.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        class="flex items-end gap-1 overflow-x-auto pt-1 pb-0"
        role="tablist"
        aria-label="Groups"
      >
        <div
          v-for="groupSection in groupedByGroupAndFolder"
          :key="groupSection.id"
          class="flex items-center gap-1 shrink-0 border border-b-0 rounded-t-md px-2 transition-all"
          :class="
            selectedGroupTabId === groupSection.id
              ? 'bg-primary border-primary text-primary-contrast shadow-sm py-2 min-h-11'
              : 'bg-surface-100 border-surface-300 cursor-pointer py-1 min-h-8'
          "
          role="tab"
          :aria-selected="selectedGroupTabId === groupSection.id"
          @click="handleSelectGroupTab(groupSection.id)"
        >
          <i :class="['pi', groupSection.isPersonal ? 'pi pi-user' : 'pi pi-users', 'text-sm']" />
          <span
            class="font-medium whitespace-nowrap"
            :class="selectedGroupTabId === groupSection.id ? 'text-sm' : 'text-xs'"
            >{{ groupSection.name }}</span
          >
          <Button
            v-if="selectedGroupTabId === groupSection.id && groupSection.isOwnedByCurrentUser"
            icon="pi pi-plus"
            size="small"
            class="!bg-white !text-primary !border !border-primary !w-6 !h-6 !p-0 !rounded-sm"
            @click.stop="
              (handleSelectGroupTab(groupSection.id), handleCreateInGroup(groupSection.id))
            "
          />
        </div>
      </div>

      <div
        v-if="selectedGroupSection"
        class="border border-surface rounded-b-md rounded-tr-md bg-surface-0 p-4"
      >
        <div class="flex items-center gap-3 mb-4">
          <i
            :class="[
              'pi',
              selectedGroupSection.isPersonal ? 'pi-user' : 'pi-users',
              'text-xl text-primary',
            ]"
          />
          <div>
            <h2 class="text-xl font-semibold">{{ selectedGroupSection.name }}</h2>
            <p class="text-sm text-surface-500">
              {{ selectedGroupSection.count }}
              {{ selectedGroupSection.count === 1 ? 'password' : 'passwords' }}
            </p>
          </div>
        </div>

        <div class="space-y-2 mt-4 pt-4 border-t border-surface">
          <FolderCard
            v-for="folder in selectedGroupSection.folders"
            :key="`${selectedGroupSection.id}-${folder.name}`"
            :folder="folder"
            :contextGroupId="selectedGroupSection.id"
            :isOpen="openFolderKey === `${selectedGroupSection.id}-${folder.name}`"
            @toggle="handleFolderToggle(`${selectedGroupSection.id}-${folder.name}`)"
            @edit="handleEdit"
            @share="handleShare"
            @history="handleHistory"
            @deleted="handleDeleted"
          />
        </div>
      </div>
    </div>

    <!-- Modals -->
    <CreatePasswordModal
      v-model:visible="showCreateModal"
      :editPassword="editingPassword"
      :defaultGroupId="defaultCreateGroupId"
      @created="handlePasswordCreated"
      @updated="handlePasswordUpdated"
    />

    <SharePasswordModal
      v-model:visible="showShareModal"
      :password="sharingPassword"
      @shared="handleShared"
      @unshared="handleUnshared"
    />

    <PasswordHistoryModal v-model:visible="showHistoryModal" :password="historyPassword" />
  </div>
</template>
