<script setup lang="ts">
import type { ContextMenuItem } from '@nuxt/ui'
import type { FolderItem } from '~/shared/types/folderItem'
import { ref } from 'vue'

const router = useRouter()

const { data, pending, error } = await useFetch<FolderItem[]>('/api/folders/list')

const menuItems = ref<ContextMenuItem[][]>([
  [
    { label: 'New folder', icon: 'i-lucide-plus', disabled: true },
    {
      label: 'Appearance',
      children: [
        { label: 'System', icon: 'i-lucide-monitor' },
        { label: 'Light', icon: 'i-lucide-sun' },
        { label: 'Dark', icon: 'i-lucide-moon' },
      ],
    },
  ],
  [
    { label: 'Rename', kbds: ['ctrl', 'r'], disabled: true },
    { label: 'Permissions', kbds: ['shift', 'meta', 'd'] },
    { label: 'Show properties', disabled: true },
  ],
  [{ label: 'Delete', icon: 'i-lucide-trash' }],
])

/**
 * Recursively build path to item
 */
function buildItemPath(
  item: FolderItem,
  currentItems: FolderItem[] = data.value ?? [],
  path: string[] = [],
): string[] | null {
  for (const node of currentItems) {
    const newPath = [...path, node.slug]

    if (node.slug === item.slug && node.children === item.children)
      return newPath

    if (node.children) {
      const result = buildItemPath(item, node.children as FolderItem[], newPath)
      if (result)
        return result
    }
  }
  return null
}

function handleItemClick(item: any) {
  const fullPath = buildItemPath(item)
  if (fullPath) {
    const encodedPath = fullPath.map(encodeURIComponent).join('/')
    router.push(`/passwords/${encodedPath}`)
  }
}
</script>

<template>
  <div v-if="pending">
    <UProgress orientation="vertical" class="h-48" />
  </div>
  <div v-else-if="error">
    Error: {{ error.message }}
  </div>
  <UTree v-else size="xl" :items="data">
    <template #item="{ item, expanded }">
      <UContextMenu :items="menuItems">
        <div class="flex items-center justify-between w-full cursor-pointer  transition-colors">
          <!-- Left: Context menu trigger + icons -->
          <div class="flex items-center rounded-xl w-full" @click="handleItemClick(item)">
            <UIcon v-if="expanded" name="i-lucide-folder-open" />
            <UIcon v-else name="i-lucide-folder" />
            <span class="ml-2 flex items-center">
              {{ item.label }}
              <UIcon v-if="item.icon" :name="item.icon" class="text-lg ml-2" />
            </span>
          </div>
          <!-- Right: Chevron for expanding/collapsing -->
          <UIcon
            v-if="item.children" name="i-lucide-chevron-down"
            class="w-4 h-4 mr-3 transform transition-transform duration-200" :class="[{ 'rotate-180': expanded }]"
          />
        </div>
      </UContextMenu>
    </template>
  </UTree>
</template>
