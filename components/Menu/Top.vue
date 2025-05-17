<script setup lang="ts">
import type { ContextMenuItem } from "@nuxt/ui";
import { ref } from "vue";

const items = ref([
  {
    label: "First folder",
    defaultExpanded: true,
    children: [
      {
        label: "1-1",
        icon: "i-vscode-icons-file-type-typescript",
        children: [
          { label: "useAuth.ts", icon: "i-vscode-icons-file-type-typescript" },
          { label: "useUser.ts", icon: "i-vscode-icons-file-type-typescript" },
        ],
      },
      {
        label: "1-2",
        defaultExpanded: true,
        children: [
          { label: "1-2-1", icon: "i-vscode-icons-file-type-vue" },
          { label: "1-2-2", icon: "i-vscode-icons-file-type-vue" },
        ],
      },
    ],
  },
  { label: "Second folder", icon: "i-vscode-icons-file-type-vue" },
  { label: "Third folder", icon: "i-vscode-icons-file-type-nuxt" },
]);

const menuItems = ref<ContextMenuItem[][]>([
  [
    {
      label: "Appearance",
      children: [
        { label: "System", icon: "i-lucide-monitor" },
        { label: "Light", icon: "i-lucide-sun" },
        { label: "Dark", icon: "i-lucide-moon" },
      ],
    },
  ],
  [
    { label: "Rename", kbds: ["ctrl", "r"], disabled: true },
    { label: "Permissions", kbds: ["shift", "meta", "d"] },
    { label: "Show properties", disabled: true },
  ],
  [{ label: "Delete", icon: "i-lucide-trash" }],
]);
</script>

<template>
  <UTree :items="items">
    <template #item="{ item, level, expanded, selected }">
      <div :class="[
          'flex items-center justify-between w-full rounded-xl transition-colors',
          selected ? 'bg-gray-200' : 'hover:bg-gray-100',
        ]">
        <!-- Left: Context menu trigger + icons -->
        <div class="flex items-center">
          <UContextMenu :items="menuItems">
            <div class="flex items-center cursor-pointer p-3">
              <UIcon v-if="expanded" name="i-lucide-folder-open" />
              <UIcon v-else name="i-lucide-folder" />

              <span class="ml-2 flex items-center">
                {{ item.label }}
                <UIcon v-if="item.icon" :name="item.icon" class="text-lg ml-2" />
              </span>
            </div>
          </UContextMenu>
        </div>

        <!-- Right: Chevron for expanding/collapsing -->
        <UIcon v-if="item.children" name="i-lucide-chevron-down"
          class="w-4 h-4 mr-3 transform transition-transform duration-200" :class="[{ 'rotate-180': expanded }]"/>
      </div>
    </template>
  </UTree>
</template>
