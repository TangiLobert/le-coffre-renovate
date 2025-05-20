import type { FolderItem } from '~/shared/types/folderItem'

export default defineEventHandler((_event) => {
  // Dummy return to mockup the API
  const folderItems: FolderItem[] = [
    {
      label: 'First folder',
      slug: 'first-folder',
      defaultExpanded: true,
      children: [
        {
          label: '1-1',
          slug: '1-1',
          icon: 'i-vscode-icons-file-type-typescript',
          children: [
            { label: 'useAuth.ts', icon: 'i-vscode-icons-file-type-typescript' },
            { label: 'useUser.ts', icon: 'i-vscode-icons-file-type-typescript' },
          ],
        },
        {
          label: '1-2',
          slug: '1-2',
          defaultExpanded: true,
          children: [
            { label: '1-2-1', slug: '1-2-1', icon: 'i-vscode-icons-file-type-vue' },
            { label: '1-2-2', slug: '1-2-2', icon: 'i-vscode-icons-file-type-vue' },
          ],
        },
      ],
    },
    { label: 'Second folder', slug: 'second-folder', icon: 'i-vscode-icons-file-type-vue' },
    { label: 'Third folder', slug: 'third-folder', icon: 'i-vscode-icons-file-type-nuxt' },
  ]

  return folderItems
})
