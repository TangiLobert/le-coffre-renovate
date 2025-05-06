import { eq } from 'drizzle-orm'
import { useDatabase } from '~/composables/useDatabase'
import { globalConfig } from '~/server/database/schema'

export enum ConfigKey {
  SetupCompleted = 'setup_completed',
}

type ConfigValue = string | number | boolean | object | null

const storage = useStorage<ConfigValue>('kv:global-config')

export async function getConfiguration(key: ConfigKey): Promise<ConfigValue> {
  const cached = await storage.getItem<ConfigValue>(key)
  if (cached != null) {
    return cached
  }

  // Cache miss, fetch from database
  const result = useDatabase().select().from(globalConfig).where(eq(globalConfig.name, key)).get()

  if (result) {
    await storage.setItem(key, result.value as ConfigValue)
    return result.value as ConfigValue
  }

  return null as ConfigValue
}

export async function setConfiguration(key: ConfigKey, value: ConfigValue): Promise<void> {
  const db = useDatabase()
  const existing = db.select().from(globalConfig).where(eq(globalConfig.name, key)).get()

  if (existing) {
    db.update(globalConfig).set({ value }).where(eq(globalConfig.name, key)).run()
  }
  else {
    db.insert(globalConfig).values({ name: key, value }).run()
  }

  await storage.setItem(key, value)
}

export async function isSetupCompleted() {
  const setupCompleted = await getConfiguration(ConfigKey.SetupCompleted)
  return setupCompleted === 'true'
}

export async function insertInitialData() {
  const initialData = [
    { name: ConfigKey.SetupCompleted, value: 'false' },
  ]

  await useDatabase()
    .insert(globalConfig)
    .values(initialData)
}
