import type { GroupItem } from '@/client/types.gen'

export type GroupSortMode = 'name' | 'count'

/**
 * Sort groups alphabetically, personal group first if present in the list.
 */
export function sortGroupsByName(groups: GroupItem[]): GroupItem[] {
  return [...groups].sort((a, b) => {
    if (a.is_personal && !b.is_personal) return -1
    if (!a.is_personal && b.is_personal) return 1
    return a.name.localeCompare(b.name)
  })
}

/**
 * Sort groups by password count descending; personal group is always first regardless of count.
 * Ties between non-personal groups broken alphabetically.
 */
export function sortGroupsByCount(
  groups: GroupItem[],
  passwordCounts: Record<string, number>,
): GroupItem[] {
  return [...groups].sort((a, b) => {
    if (a.is_personal && !b.is_personal) return -1
    if (!a.is_personal && b.is_personal) return 1
    const countA = passwordCounts[a.id] ?? 0
    const countB = passwordCounts[b.id] ?? 0
    if (countB !== countA) return countB - countA
    return a.name.localeCompare(b.name)
  })
}

/**
 * Sort groups according to the given mode.
 * Falls back to name sort if mode is 'count' but no counts are provided.
 */
export function sortGroups(
  groups: GroupItem[],
  mode: GroupSortMode,
  passwordCounts?: Record<string, number>,
): GroupItem[] {
  if (mode === 'count' && passwordCounts) {
    return sortGroupsByCount(groups, passwordCounts)
  }
  return sortGroupsByName(groups)
}
