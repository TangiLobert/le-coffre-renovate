import { consola } from 'consola'

export async function isSealed(): Promise<boolean> {
  consola.info('Checking if the database is sealed...')
  return false
}

export async function sealDatabase(): Promise<void> {
  consola.info('Sealing the database...')
}

export async function unsealDatabase(): Promise<void> {
  consola.info('Unsealing the database...')
}
